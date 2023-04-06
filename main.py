from dotenv import load_dotenv
import os

# 加载配置文件
load_dotenv()

OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL')
OPENAI_CHAT_URL = os.getenv('OPENAI_CHAT_URL')
OPENAI_EMBEDDING_URL = os.getenv('OPENAI_EMBEDDING_URL')
OPENAI_MAX_RETRY = os.getenv('OPENAI_MAX_RETRY')
OPENAI_TIMEOUT = os.getenv('OPENAI_TIMEOUT')
