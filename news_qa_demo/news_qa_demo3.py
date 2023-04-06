import numpy as np
import pandas as pd
import token_calculator_demo.token_calculator as tc
import main
import utils.openai_utils as ou
from openai.embeddings_utils import cosine_similarity
from openai.embeddings_utils import distances_from_embeddings
import re

COMPLETIONS_MODEL = main.OPENAI_CHAT_MODEL
EMBEDDING_MODEL = main.OPENAI_EMBEDDING_MODEL
MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
separator_len = tc.num_tokens_from_string(SEPARATOR, COMPLETIONS_MODEL)
# news_export_test.csv, news_export_20230329110411.csv,
original_file_name = "news_export_20230329110411.csv"
# news_export_test_token.csv
token_file_name = "news_export_20230329110411_token.csv"

embedding_file_name = "news_export_20230329110411_embedding3.csv"

max_token = 500


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    return ou.embedding(text, model, 20)


def construct_prompt(question: str, df: pd.DataFrame) -> str:
    """
    Fetch relevant
    """
    query_embedding = get_embedding(question)

    # Get the distances from the embeddings
    df["distances"] = distances_from_embeddings(query_embedding, [eval(x) for x in df["embeddings"].values],
                                                distance_metric="cosine")

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for row_index, row in df.sort_values('distances', ascending=True).iterrows():
        # Add contexts until we run out of space.
        chosen_sections_len += tc.num_tokens_from_string(row["content"], COMPLETIONS_MODEL) + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break
        chosen_sections.append(SEPARATOR + row["content"].replace("\n", " "))
        chosen_sections_indexes.append(str(row_index))

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))

    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not 
    contained within the text below, say "I don't know. And also remember the answer should be the same language of the question."\n\nContext:\n """

    return header + "".join(chosen_sections) + "\n\n Question: " + question + "\n Answer:"


# Function to split the text into chunks of a maximum number of tokens
def get_news_content(content, token_threshold):
    file_contents = []
    token_num = tc.num_tokens_from_string(content, COMPLETIONS_MODEL)

    # 判断token长度，如果大于阈值，则按照段落拆分，让组合的段落 token 小于阈值, 如果一个段落已经大于 阈值 了，则按照句子拆分。
    if token_num > token_threshold:
        lines = content.split("\n")
        file_content_chunk = ''
        for i, line in enumerate(lines):
            # 如果段落过长，则按照句子拆分，逻辑同理
            if tc.num_tokens_from_string(line, COMPLETIONS_MODEL) > token_threshold:
                print("line too long")
                sentences = re.split('[.。]', line)
                for j, sentence in enumerate(sentences):
                    # 如果段落过长，则按照句子拆分，逻辑同理
                    if tc.num_tokens_from_string(sentence, COMPLETIONS_MODEL) > token_threshold:
                        print("sentence too long")
                    else:
                        if tc.num_tokens_from_string(file_content_chunk + sentence,
                                                     COMPLETIONS_MODEL) > token_threshold:
                            file_contents.append(file_content_chunk + " ")
                            file_content_chunk = ''
                            file_content_chunk += sentence
                        else:
                            file_content_chunk += sentence
                        if j == len(sentences) - 1:
                            file_contents.append(file_content_chunk + " ")
                            file_content_chunk = ''

            else:
                if tc.num_tokens_from_string(file_content_chunk + line, COMPLETIONS_MODEL) > token_threshold:
                    file_contents.append(file_content_chunk + " ")
                    file_content_chunk = ''
                    file_content_chunk += line
                else:
                    file_content_chunk += line
                if i == len(lines) - 1:
                    file_contents.append(file_content_chunk + " ")
                    file_content_chunk = ''
    else:
        file_contents.append(content)
    return file_contents


def generate_chunk_file(file_name: str, original_df: pd.DataFrame):
    new_df = pd.DataFrame(columns=["news_id", "content", "embeddings", "token"])
    for _, row in original_df.iterrows():
        # 标题
        new_row = {"news_id": row["news_id"], "content": row["title"], "embeddings": get_embedding(row["title"]),
                   "token": tc.num_tokens_from_string(row["title"], COMPLETIONS_MODEL)}
        new_df.loc[len(new_df)] = new_row

        # 正文
        chunks = get_news_content(row["content"], max_token)
        for chunk in chunks:
            chunk = chunk.replace("\n", " ")
            new_row = {"news_id": row["news_id"], "content": chunk, "embeddings": get_embedding(chunk),
                       "token": tc.num_tokens_from_string(chunk, COMPLETIONS_MODEL)}
            new_df.loc[len(new_df)] = new_row
    new_df.to_csv(file_name, index=False, encoding="UTF-8")


def answer_query_with_context(query: str, df: pd.DataFrame,
                              show_prompt: bool = False) -> str:
    final_prompt = construct_prompt(query, df)
    if show_prompt:
        print(final_prompt)
    message = [{"role": "system", "content": "You are a great assistant，Your name is \\\"Synapse AI\\\""},
               {"role": "user", "content": final_prompt}]
    response = ou.chat_completion(message, max_tokens=1200, temperature=0.0, timeout=20)
    return response


# 生成 embedding 文件
'''
2 - 标题加入向量，单独成为一行
3 - 将正文内容按照不大于 MAX TOKEN 的长度拆分，分开算向量
'''
# my_df = pd.read_csv(original_file_name)
# print(f"{len(my_df)} rows in the data.")
# generate_chunk_file(embedding_file_name, my_df)

my_df = pd.read_csv(embedding_file_name)
print(f"{len(my_df)} rows in the data.")

# 读取用户输入
input_str = input("Synapse 智能机器人： 你好，我是 Synapse 智能机器人，你有什么想问的吗？（输入 'q' 或 'quit' 退出程序）：")
result = ([], '')
count = 0
while True:
    if count > 0:
        input_str = input("Synapse 智能机器人： 请继续提问？（输入 'q' 或 'quit' 退出程序）：")
    # 如果用户输入 'q' 或 'quit'，则退出循环
    if input_str.lower() in ['q', 'quit']:
        break
    try:
        # 有限多轮，可以实现问答
        # result = answer_question(df, question=input_str.split(), previous_message=result[0], debug=False)

        # 完全多轮，可以实现有记忆的问答
        result = answer_query_with_context(input_str, my_df, True)
        print(result)
        count += 1
    except Exception as e:
        print(e)
        print("输入错误，请重新输入。")
