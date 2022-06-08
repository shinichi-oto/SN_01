# Hugging_Face

from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")


def fugging_translation(article, translate="en"):
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

    if translate == "jp":
        tokenizer.src_lang = "ja_XX"
        lang_code = tokenizer.lang_code_to_id["en_XX"]
    elif translate == "en":
        tokenizer.src_lang = "en_XX"
        lang_code = tokenizer.lang_code_to_id["ja_XX"]
    encode = tokenizer(article, return_tensors="pt")
    generate = model.generate(
        **encode,
        forced_bos_token_id=lang_code
    )
    return generate, tokenizer


def translate_decode(tokenizers, generated):
    trans = tokenizers.batch_decode(generated, skip_special_tokens=True)
    return trans
