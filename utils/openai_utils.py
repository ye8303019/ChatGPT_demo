import openai_key
import requests
import json
import utils.json_utils as ju
import main
from requests.exceptions import Timeout

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + openai_key.api_key
}


# OpenAI - Complete
def chat_completion(message, model='gpt-3.5-turbo', max_tokens=1000, temperature=0.2, timeout=int(main.OPENAI_TIMEOUT)):
    payload = {
        "model": model,
        "messages": message,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    max_retries = int(main.OPENAI_MAX_RETRY)

    for retry in range(max_retries):
        try:
            response = requests.post(main.OPENAI_CHAT_URL, headers=headers, data=json.dumps(payload),
                                     timeout=timeout)
            result = ju.json2dict(response.content.decode())["choices"][0]["message"]["content"]
            response.raise_for_status()  # 检查响应状态码
            break  # 如果请求成功，跳出重试循环
        except Timeout:
            print(f"请求超时（第{retry + 1}次重试）")
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误：{e}")
        if retry == max_retries - 1:
            print("已达到最大重试次数，无法完成请求")

    return result.strip()


# OpenAI - Embedding
def embedding(content, model='text-embedding-ada-002', timeout=int(main.OPENAI_TIMEOUT)):
    payload = {
        "model": model,
        "input": content
    }

    max_retries = int(main.OPENAI_MAX_RETRY)

    for retry in range(max_retries):
        try:
            response = requests.post(main.OPENAI_EMBEDDING_URL, headers=headers, data=json.dumps(payload),
                                     timeout=timeout)
            result = ju.json2dict(response.content.decode())["data"][0]["embedding"]
            response.raise_for_status()  # 检查响应状态码
            break  # 如果请求成功，跳出重试循环
        except Timeout:
            print(f"请求超时（第{retry + 1}次重试）")
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误：{e}")
        if retry == max_retries - 1:
            print("已达到最大重试次数，无法完成请求")

    return result
