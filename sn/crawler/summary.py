from transformers import PegasusTokenizer, PegasusForConditionalGeneration


#model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
#tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-xsum")


def fugging_summary(text):
    model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
    tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-xsum")

    inputs = tokenizer([text], return_tensors='pt', truncation=True)
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=200, early_stopping=True)
    generate_text = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                     summary_ids]
    return generate_text[0]

