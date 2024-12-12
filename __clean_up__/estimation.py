# OpenAI tokenizer
from tiktoken import encoding_for_model
# Llama tokenizer
from transformers import LlamaTokenizer

def estimated_cost(text, model):
    num_tokens = number_of_tokens(text, model)
    # Different costs based on model
    cost_per_million_tokens = 10
    return num_tokens / 1000000 * cost_per_million_tokens

def number_of_tokens(text, model):
    if model.lower().contains("openai"):
        encoding = encoding_for_model(model)
        return len(encoding.encode(text))
    elif model.lower().contains("llama"):
        tokenizer = LlamaTokenizer.from_pretrained(model)
        return len(tokenizer.encode(text))
    elif model.lower().contains("claude"):
        return len(text) / 4
    else:
        raise ValueError(f"Unsupported model: {model}")

