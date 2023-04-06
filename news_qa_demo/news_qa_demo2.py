import numpy as np
import pandas as pd
import token_calculator_demo.token_calculator as tc
import main
import utils.openai_utils as ou
from openai.embeddings_utils import cosine_similarity
from openai.embeddings_utils import distances_from_embeddings

COMPLETIONS_MODEL = main.OPENAI_CHAT_MODEL
EMBEDDING_MODEL = main.OPENAI_EMBEDDING_MODEL
MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
separator_len = tc.num_tokens_from_string(SEPARATOR, COMPLETIONS_MODEL)
# news_export_test.csv, news_export_20230329110411.csv,
original_file_name = "news_export_20230329110411.csv"
# news_export_test_token.csv
token_file_name = "news_export_20230329110411_token.csv"

embedding_file_name = "news_export_20230329110411_embedding2.csv"

file_index = ["news_id", "title"]
my_question = "What's the risks for mental health crises?"


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    return ou.embedding(text, model, 20)


def compute_doc_embeddings(df: pd.DataFrame) -> dict[tuple[str, str], list[float]]:
    """
    Create an embedding for each row in the dataframe using the OpenAI Embeddings API.

    Return a dictionary that maps between each embedding vector and the index of the row that it corresponds to.
    """
    return {
        idx: get_embedding(r.content) for idx, r in df.iterrows()
    }


def vector_similarity(x: list[float], y: list[float]) -> float:
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(query: str, contexts: dict[(str, str), np.array]) -> list[
    (float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)

    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)

    return document_similarities


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


def load_embeddings(file_name: str) -> dict[tuple[str, str], list[float]]:
    """
    Read the document embeddings and their keys from a CSV.

    fname is the path to a CSV with exactly these named columns:
        "title", "heading", "0", "1", ... up to the length of the embedding vectors.
    """

    df = pd.read_csv(file_name, header=0)
    max_dim = max([int(c) for c in df.columns if (c and c not in file_index)])
    return {
        (r[file_index[0]], r[file_index[1]]): [r[str(i)] for i in range(max_dim + 1)] for _, r in df.iterrows()
    }


def add_token(file_name: str, df: pd.DataFrame):
    my_df["token"] = [tc.num_tokens_from_string(c, COMPLETIONS_MODEL) for c in df["content"]]
    my_df.to_csv(file_name, index=True, index_label=file_index, encoding="UTF-8")


def add_embedding(file_name: str, df: pd.DataFrame):
    df["embeddings"] = df.content.apply(lambda x: get_embedding(x))
    df.to_csv(file_name, index=True, index_label=file_index, encoding="UTF-8")


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
# my_df = pd.read_csv(original_file_name)
# my_df = my_df.set_index(file_index)
# print(f"{len(my_df)} rows in the data.")
# # add_token(token_file_name, my_df)
# add_embedding(embedding_file_name, my_df)


my_df = pd.read_csv(embedding_file_name)
my_df = my_df.set_index(file_index)
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
