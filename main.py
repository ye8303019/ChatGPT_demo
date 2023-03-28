from dotenv import load_dotenv
import os

# 加载配置文件
load_dotenv()

OPENAI_MODEL = os.getenv('OPENAI_MODEL')
OPENAI_URL = os.getenv('OPENAI_URL')
OPENAI_MAX_RETRY = os.getenv('OPENAI_MAX_RETRY')
OPENAI_TIMEOUT = os.getenv('OPENAI_TIMEOUT')
