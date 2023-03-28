import token_calculator_demo.token_calculator as tc
import re


def get_file_content(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        # Read the file content and store it in a variable
        file_content = file.read()
    return file_content


# split the file content into a reasonable chunks
def get_file_contents(file_content, token_threshold=1000, model='gpt-3.5-turbo'):
    file_contents = []
    token_num = tc.num_tokens_from_string(file_content, model)

    # 判断token长度，如果大于阈值，则按照段落拆分，让组合的段落 token 小于阈值, 如果一个段落已经大于 阈值 了，则按照句子拆分。
    if token_num > token_threshold:
        lines = file_content.split("\n")
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
        file_contents.append(file_content)
    return file_contents
