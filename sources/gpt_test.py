from transformers import (
    GPT2Tokenizer, 
    GPT2LMHeadModel
)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
prefix = "<|endoftext|>"
prompt_text = "A random"

encoded_prompt = tokenizer(prefix + ' ' + prompt_text,
                           add_special_tokens=False)
print("\nIDs with <prefix, space, prompt, manual special>:\n", encoded_prompt.input_ids)

encoded_prompt = tokenizer(prefix + prompt_text, add_special_tokens=False)
print("\nIDs with <prefix, nospace, prompt, manual special>:\n", encoded_prompt.input_ids)
out_1 = model(tokenizer.encode(prefix + prompt_text, add_special_tokens=False, return_tensors="pt"))
print("Logits with <prefix, nospace, prompt, manual special>:\n", out_1.logits)

encoded_prompt = tokenizer(prompt_text)
print(encoded_prompt.input_ids)
print("\nIDs with <prompt>:\n", encoded_prompt.input_ids)
out_2 = model(tokenizer.encode(prompt_text, return_tensors="pt"))
print("Logits with <prompt>:\n", out_2.logits)

print("\nIDs with <manualprefix, prompt>:\n", [tokenizer.bos_token_id] + tokenizer(prompt_text).input_ids)
out_3 = model(tokenizer.encode([tokenizer.bos_token_id] + tokenizer(prompt_text).input_ids, return_tensors="pt"))
print("Logits with <manualprefix, prompt>:\n", out_3.logits)
