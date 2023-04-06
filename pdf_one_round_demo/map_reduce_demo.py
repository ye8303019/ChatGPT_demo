import openai
import PyPDF2
import re
import token_calculator_demo.token_calculator as tc
import openai_key
import main
import utils.openai_utils as ou

openai.api_key = openai_key.api_key

# Author : Ye Zhongkai

# 2302.10205.pdf, 2302.09419.pdf, Rethinking-Marketing(1).pdf, mv-v19-1074.pdf
file_name = 'Rethinking-Marketing(1).pdf'
pdf_chunk_token_limit = 3200
map_character_limit = 650
reduce_character_limit = 3300
model = main.OPENAI_CHAT_MODEL


# Remove new lines from the text
def remove_newlines(series):
    series = series.replace('\n', ' ')
    series = series.replace('\\n', ' ')
    series = series.replace('  ', ' ')
    series = series.replace('  ', ' ')
    return series


def get_pdf_content(pdf_file_name):
    # Open the PDF file
    pdf_file = open(pdf_file_name, 'rb')

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

    # Close the PDF file
    pdf_file.close()

    return pdf_text


def get_pdf_chunks(pdf_text, token_threshold):
    file_contents = []
    # Open the file in read mode
    token_num = tc.num_tokens_from_string(pdf_text, model)

    # 判断token长度，如果大于阈值，则按照段落拆分，让组合的段落 token 小于阈值, 如果一个段落已经大于 阈值 了，则按照句子拆分。
    if token_num > token_threshold:
        lines = pdf_text.split("\n")
        file_content_chunk = ''
        for i, line in enumerate(lines):
            # 如果段落过长，则按照句子拆分，逻辑同理
            if tc.num_tokens_from_string(line, model) > token_threshold:
                print("line too long")
                sentences = re.split('[.。]', line)
                for j, sentence in enumerate(sentences):
                    # 如果段落过长，则按照句子拆分，逻辑同理
                    if tc.num_tokens_from_string(sentence, model) > token_threshold:
                        print("sentence too long")
                    else:
                        if tc.num_tokens_from_string(file_content_chunk + sentence, model) > token_threshold:
                            file_contents.append(file_content_chunk + " ")
                            file_content_chunk = ''
                            file_content_chunk += sentence
                        else:
                            file_content_chunk += sentence
                        if j == len(sentences) - 1:
                            file_contents.append(file_content_chunk + " ")
                            file_content_chunk = ''

            else:
                if tc.num_tokens_from_string(file_content_chunk + line, model) > token_threshold:
                    file_contents.append(file_content_chunk + " ")
                    file_content_chunk = ''
                    file_content_chunk += line
                else:
                    file_content_chunk += line
                if i == len(lines) - 1:
                    file_contents.append(file_content_chunk + " ")
                    file_content_chunk = ''
    else:
        file_contents.append(pdf_text)
    return file_contents


def map_prompt(chunk_content):
    message = [{"role": "system", "content": "You are a research analyst"},
               {"role": "user", "content": "I will provide you with a section of a document and you will "
                                           "create a summary from it. You will use your editing and writing "
                                           "skills to create a summary in the style of a Confidential "
                                           "Information Memorandum. You will preserve as many details as "
                                           "possible. You will maintain context across the summary. Your "
                                           "section will be combined with the other sections to create "
                                           "summary of the entire document. Do you understand?"},
               {"role": "assistant", "content": "Yes, I understand. Please provide the section of the "
                                                "document for me to summarize."},
               {"role": "user", "content": f"Your summary must be no longer than {map_character_limit} characters long."
                                           f"Input: {chunk_content} "
                                           f"Output:"
                }]
    response = ou.chat_completion(message, model, map_character_limit, 0.2, 20)
    print("Map:    " + response)
    return response


def reduce_prompt(chunk_summarize_content):
    message = [{"role": "system", "content": "You are a copyeditor."},
               {"role": "user", "content": f"Combine the below summaries. The combined output must be "
                                           f"less than {reduce_character_limit} characters long. "
                                           f"You must keep the content "
                                           f"and context preserved."
                                           f"Input: {chunk_summarize_content} "
                                           f"Output:"
                }]
    response = ou.chat_completion(message, model, reduce_character_limit, 0.2, 50)
    print("Reduce:     " + response)
    return response


pdf_content = get_pdf_content(file_name)
pdf_contents = get_pdf_chunks(pdf_content, pdf_chunk_token_limit)
print("*******************   Turn PDF into %d pieces, each piece in %d tokens  ************" % (len(pdf_contents), pdf_chunk_token_limit))
map_summarized_chunks = [map_prompt(x) for x in pdf_contents]
map_summarized_chunk = ""
for i, x in enumerate(map_summarized_chunks):
    if i == 0:
        map_summarized_chunk = x
        continue
    else:
        map_summarized_chunk = reduce_prompt(map_summarized_chunk + x)

print("Final summary is: ")
print(map_summarized_chunk)
