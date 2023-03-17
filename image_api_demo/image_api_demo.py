import openai
import openai_key
from PIL import Image
import requests
from io import BytesIO
import re

openai.api_key = openai_key.api_key
question = "给我5只猫"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "现在你是一个很棒的图片搜索引擎"},
        {"role": "user", "content": "让你发图的时候，请用 markdown, 使用 unsplash API "
                                    "https://source.unsplash.com/960*640/?<英文关键词>，不要用代码块，反斜线，如果你明白回复OK就好"},
        {"role": "assistant", "content": "OK，我明白了。"},
        {"role": "user", "content": question},
    ],
    temperature=0
)
answer = response["choices"][0]["message"]["content"].strip()

urls = re.findall(r'\((.*?)\)', answer)
for item in zip(range(0, len(urls)), urls):
    print("第 %d 张图片， URL为 %s" % (item[0]+1, item[1]))
    response = requests.get(item[1])
    img = Image.open(BytesIO(response.content))
    img.show()
