from PIL import Image
import requests
from io import BytesIO
import re
import utils.openai_utils as ou

question = "给我5个建筑物的图片"


message = [
    {"role": "system", "content": "现在你是一个很棒的图片搜索引擎"},
    {"role": "user", "content": "让你发图的时候，请用 markdown, 使用 unsplash API "
                                "https://source.unsplash.com/960*640/?<英文关键词>，不要用代码块，反斜线，如果你明白回复OK就好"},
    {"role": "assistant", "content": "OK，我明白了。"},
    {"role": "user", "content": question},
]
answer = ou.chat_completion(message, temperature=0.0)

urls = re.findall(r'\((.*?)\)', answer)
for item in zip(range(0, len(urls)), urls):
    print("第 %d 张图片， URL为 %s" % (item[0] + 1, item[1]))
    response = requests.get(item[1])
    img = Image.open(BytesIO(response.content))
    img.show()
