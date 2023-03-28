import openai
import pandas as pd
import tiktoken
import PyPDF2
from openai.embeddings_utils import distances_from_embeddings
import openai_key
import main
import utils.openai_utils as ou

openai.api_key = openai_key.api_key

# Author : Ye Zhongkai

max_token = 500
# test.pdf, mv-v19-1074.pdf
file_name = 'mv-v19-1074.pdf'

model = main.OPENAI_MODEL

# Load the tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.encoding_for_model(model)


# Remove new lines from the text
def remove_newlines(series):
    series = series.replace('\n', ' ')
    series = series.replace('\\n', ' ')
    series = series.replace('  ', ' ')
    series = series.replace('  ', ' ')
    return series


# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens=max_token):
    # Split the text into sentences
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks


def create_context(question, dataframe, max_len=1800, size="ada"):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    dataframe['distances'] = distances_from_embeddings(q_embeddings, dataframe['embeddings'].values,
                                                       distance_metric='cosine')

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in dataframe.sort_values('distances', ascending=True).iterrows():

        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
        dataframe,
        models=model,
        question="Am I allowed to publish model outputs to Twitter, without a human review?",
        previous_message=[],
        max_len=1800,
        size="ada",
        debug=False,
        max_tokens=150,
        stop_sequence=None,
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        dataframe,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        message = []
        if len(previous_message) != 0:
            message = previous_message
            message.append({"role": "user", "content": f"Answer the question based on the context below, "
                                                       f"and if the question can't be answered based on "
                                                       f"the context, say \"I don't know\"\n\nContext: "
                                                       f"{context}\n\n---\n\nQuestion: {question}"})
        else:
            message.append({"role": "system", "content": "You are a great Pharmaceutical Researcher, "
                                                         "your name is \\\"Synapse AI Assistant\\\""})
            message.append({"role": "user", "content": """i will give you some context and instruction, and remember your 
                            name is \\\"Synapse AI Assistant\\\", Do you understand? """})
            message.append({"role": "system",
                            "content": f"Answer the question based on the context below, and if the question can't be "
                                       f"answered based on the context, say \"I don't know\"\n\nContext: {context}"})
            message.append({"role": "user", "content": f"Question: {question}, and please reply in the "
                                                       f"language of the question, the max length of the "
                                                       f"answer should in 3000 words"})
        # Create a completions using the question and context

        answer = ou.chat_completion(message, model, 1800, 0.2, 20)

        if debug:
            print("answer\n" + answer)
            print("\n\n")

        message.append({"role": "assistant", "content": answer})
        result_tuple = (message, answer)
        return result_tuple
    except Exception as e:
        print(e)
        return ""


# Open the PDF file
pdf_file = open(file_name, 'rb')

# Create a PDF reader object
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Get the number of pages in the PDF file
num_pages = len(pdf_reader.pages)

pdf_text = ''
# Loop through each page and extract the text
for page in range(num_pages):
    # Get the page object
    pdf_page = pdf_reader.pages[page]
    # Extract the text from the page
    pdf_text = pdf_text + pdf_page.extract_text()

# Remove newline from the text
pdf_text = remove_newlines(pdf_text)

# Close the PDF file
pdf_file.close()

# Get the file token
file_token = len(tokenizer.encode(pdf_text))

# Turn the file text into shorter lines
shortened = []
if file_token > max_token:
    shortened += split_into_many(pdf_text)
else:
    shortened += pdf_text

df = pd.DataFrame(shortened, columns=['text'])
df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
df['embeddings'] = df.text.apply(
    lambda x: openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding'])

# 读取用户输入
input_str = input("Synapse 智能机器人： 你好，我是 Synapse 智能机器人，针对这篇论文你有什么想问的吗？（输入 'q' 或 'quit' 退出程序）：")
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
        result = answer_question(df, question=input_str.split(), debug=False)
        print(result[1])
        count += 1
    except:
        print("输入错误，请重新输入。")
