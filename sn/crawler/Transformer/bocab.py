import re
import string
import pathlib

import tensorflow as tf
import tensorflow_text as text
from tensorflow_text.tools.wordpiece_vocab import bert_vocab_from_dataset as bert_vocab

from tqdm import tqdm
from sklearn.model_selection import train_test_split
from janome.tokenizer import Tokenizer as janome_tokenizer

"""
tensorflow-metadata 0.29.0 は absl-py<0.13,>=0.9 を必要としますが、
あなたは absl-py 1.1.0 を持っており、これは互換性がありません。
"""


def dataset_reader():

    def text_preprocess(text):
        def replace(match):
            return unpacking_dict[match.group(0)]

        text = unpacking_en.sub(replace, text)
        return text

    def write_vocab_file(filepath, vocab):
        # directory create add
        with open(filepath, 'w', encoding='utf-8') as f:
            for token in vocab:
                print(token, file=f)

    ja_en = []
    with open('./jpn_eng/jpn.txt', 'r', encoding='utf-8') as je_data:
        ja_en += [x.rstrip().lower().split('\t')[:2] for x in tqdm(je_data.readlines())]

    unpacking_dict = {
        "i'm": "i am", "i'will": "i would", "i've": "i have", "i'll": "i will", "i'd": "i had", "it's": "it is",
        "it'll": "it will", "it'd": "it would", "you're": "you are", "you'll": "you will",
        "you'd": "you would", "you've": "you have", "he's": "he is", "he'll": "he will", "he'd": "he would",
        "she's": "she is", "she'll": "she will", "she'd": "she would",
        "we're": "we are", "we'll": "we will", "we'd": "we would", "we've": "we have", "they're": "they are",
        "they'll": "they will", "they'd": "they would", "they've": "they have", "that's": "that is",
        "that'll": "that will", "that'd": "that would", "who's": "who is", "who'll": "who will",
        "who'd": "who would", "what's": "what is", "what're": "what are", "what'll": "what will",
        "what'd": "what would", "where's": "where is", "where'll": "where will",
        "where'd": "where would", "when's": "when is", "when'll": "when will",
        "when'd": "when would", "why's": "why is", "why'll": "why will", "why'd": "why would",
        "how's": "how is", "how'll": "how will", "how'd": "how would",
        "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not", "haven't": "have not",
        "hasn't": "has not", "hadn't": "had not", "won't": "will not", "wouldn't": "would not", "don't": "do not",
        "doesn't": "does not", "didn't": "did not", "can't": "can not", "couldn't": "could not",
        "shouldn't": "should not",
        "mightn't": "might not", "mustn't": "must not", "would've": "would have", "should've": "should have",
        "could've": "could have", "might've": "might have", "must've": "must have", "kinda": "kind of",
        "lotta": "lot of",
        "outta": "out of", "gotta": "got to", "needa": "need to", "sorta": "sort of", "lemme": "let me",
        "gimme": "give me",
        "gonna": "going to", "wanna": "want to", "getcha": "get you", "shoulda": "should have", "woulda": "would have",
        "musta": "must have", "mighta": "might have", "sec": "second", "cuz": "because", "flu": "influenza"
    }
    unpacking_en = re.compile('(%s)' % '|'.join(unpacking_dict.keys()))

    string.punctuation += '、。【】「」『』…・〽（）〜？！｡：､；･'
    rem = lambda x: x.translate(str.maketrans('', '', string.punctuation))

    eng_data = [rem(text_preprocess(x[0])) for x in ja_en]
    jpn_data = [rem(x[1]) for x in ja_en]

    j_token = janome_tokenizer()
    jpn_data = [' '.join([word for word in j_token.tokenize(x, wakati=True) if word != ' ']) for x in tqdm(jpn_data)]

    eng_train, eng_test, jpn_train, jpn_test = train_test_split(eng_data, jpn_data, test_size=0.02, random_state=42)

    # if
    jp_bert_tokenizer_params = dict(lower_case=False)
    en_bert_tokenizer_params = dict(lower_case=True)

    reserved_tokens = ["[PAD]", "[UNK]", "[START]", "[END]"]

    jp_bert_vocab_args = dict(vocab_size=20000, reserved_tokens=reserved_tokens,
                              bert_tokenizer_params=jp_bert_tokenizer_params,
                              learn_params={})

    en_bert_vocab_args = dict(vocab_size=20000, reserved_tokens=reserved_tokens,
                              bert_tokenizer_params=en_bert_tokenizer_params,
                              learn_params={})

    jpn_train_tensor = tf.data.Dataset.from_tensor_slices(jpn_train)
    eng_train_tensor = tf.data.Dataset.from_tensor_slices(eng_train)

    jp_vocab = bert_vocab.bert_vocab_from_dataset(
        jpn_train_tensor.batch(1000).prefetch(tf.data.AUTOTUNE),
        **jp_bert_vocab_args
    )
    en_vocab = bert_vocab.bert_vocab_from_dataset(
        eng_train_tensor.batch(1000).prefetch(tf.data.AUTOTUNE),
        **en_bert_vocab_args
    )

    write_vocab_file('jp_vocab.txt', jp_vocab)
    write_vocab_file('en_vocab.txt', en_vocab)

    return eng_train, jpn_train


def add_start_end(ragged):
    reserved_tokens = ["[PAD]", "[UNK]", "[START]", "[END]"]

    START = tf.argmax(tf.constant(reserved_tokens) == "[START]")
    END = tf.argmax(tf.constant(reserved_tokens) == "[END]")

    count = ragged.bounding_shape()[0]
    starts = tf.fill([count, 1], START)
    ends = tf.fill([count, 1], END)
    return tf.concat([starts, ragged, ends], axis=1)


def cleanup_text(reserved_tokens, token_txt):
    # [UNK]を除く予約済みトークンを削除
    bad_tokens = [re.escape(tok) for tok in reserved_tokens if tok != "[UNK]"]
    bad_token_re = "|".join(bad_tokens)

    bad_cells = tf.strings.regex_full_match(token_txt, bad_token_re)
    result = tf.ragged.boolean_mask(token_txt, ~bad_cells)

    # Join them into strings.
    result = tf.strings.reduce_join(result, separator=' ', axis=-1)

    return result


class CustomTokenizer(tf.Module):

    def __init__(self, reserved_tokens, vocab_path):
        if vocab_path == 'en_vocab.txt':
            self.tokenizer = text.BertTokenizer(vocab_path, lower_case=True)
        else:
            self.tokenizer = text.BertTokenizer(vocab_path, lower_case=False)

        self._reserved_tokens = reserved_tokens
        self._vocab_path = tf.saved_model.Asset(vocab_path)
        vocab = pathlib.Path(vocab_path).read_text(encoding='utf8').splitlines()
        self.vocab = tf.Variable(vocab)

        self.tokenize.get_concrete_function(
            tf.TensorSpec(shape=[None], dtype=tf.string))
        self.detokenize.get_concrete_function(
            tf.TensorSpec(shape=[None, None], dtype=tf.int64))
        self.detokenize.get_concrete_function(
            tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int64))
        self.lookup.get_concrete_function(
            tf.TensorSpec(shape=[None, None], dtype=tf.int64))
        self.lookup.get_concrete_function(
            tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int64))
        self.get_vocab_size.get_concrete_function()
        self.get_vocab_path.get_concrete_function()
        self.get_reserved_tokens.get_concrete_function()

    @tf.function
    def tokenize(self, strings):
        enc = self.tokenizer.tokenize(strings)
        enc = enc.merge_dims(-2,-1)
        enc = add_start_end(enc)
        return enc

    @tf.function
    def detokenize(self, tokenized):
        words = self.tokenizer.detokenize(tokenized)
        return cleanup_text(self._reserved_tokens, words)

    @tf.function
    def lookup(self, token_ids):
        return tf.gather(self.vocab, token_ids)\

    @tf.function
    def get_vocab_size(self):
        return tf.shape(self.vocab)[0]

    @tf.function
    def get_vocab_path(self):
        return self._vocab_path

    @tf.function
    def get_reserved_tokens(self):
        return tf.constant(self._reserved_tokens)
