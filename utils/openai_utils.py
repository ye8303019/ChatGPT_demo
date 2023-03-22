import openai
import openai_key

openai.api_key = openai_key.api_key


# OpenAI - Complete
def chat_completion(message, model='gpt-3.5-turbo', max_tokens=1000, temperature=0.2):
    response = openai.ChatCompletion.create(
        model=model,
        max_tokens=max_tokens,
        messages=message,
        temperature=temperature
    )
    return response["choices"][0]["message"]["content"].strip()
