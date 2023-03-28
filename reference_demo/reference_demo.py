import openai
import utils.openai_utils as ou
import re

import main
import token_calculator_demo.token_calculator as tc
import openai_key

openai.api_key = openai_key.api_key

# Author : Ye Zhongkai

# reference_content_1
model = main.OPENAI_MODEL
table_summary_limit = 1500
table_summary_token_limit = 300
final_summary_token_limit = 2000


def get_content(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        # Read the file content and store it in a variable
        file_content = file.read()
    return file_content


def get_tables(file_content):
    # regular expression to match the start of a table
    table_start_regex = r'\[Table \d+\]'

    # regular expression to match the end of a table
    table_end_regex = r'(?=\n\[Table \d+\]|$)'

    # find all the matches for table start and end points
    table_starts = [match.end() for match in re.finditer(table_start_regex, file_content)]
    table_ends = [match.start() for match in re.finditer(table_end_regex, file_content)]

    tables = []
    for i in range(len(table_starts)):
        table_content = file_content[table_starts[i]:table_ends[i]].strip()
        tables.append(table_content)
    return tables


def split_content(file_content, token_threshold):
    tables = get_tables(file_content)
    file_contents = []
    file_content_chunk = ''
    for i, table in enumerate(tables):
        # 如果段落过长，则按照句子拆分，逻辑同理
        if tc.num_tokens_from_string(table, model) > token_threshold:
            print("table too long... ignore")
        else:
            if tc.num_tokens_from_string(file_content_chunk + table, model) > token_threshold:
                file_contents.append(file_content_chunk + " ")
                file_content_chunk = ''
                file_content_chunk += table
            else:
                file_content_chunk += table
            if i == len(tables) - 1:
                file_contents.append(file_content_chunk + " ")
                file_content_chunk = ''
    return file_contents


def get_shot_summary(content):
    if "Current date" in content:
        return content
    else:
        message = [{"role": "system", "content": "You are a great Pharmaceutical Project Analyzer"},
                   {"role": "user", "content": f"Context: \n"
                                               f"{content} \n "
                                               f"Instructions:Please explain the content above, should "
                                               f"put the real number into your explanation to give a more accurate "
                                               f"analysis. write in English and The output must be "
                                               f"less than {table_summary_limit} characters long"
                    }]
        response = ou.chat_completion(message, model, table_summary_token_limit)
        print("===============================================================")
        print("Summary: " + response)
    return response


def read_with_reference(content):
    message = [{"role": "system", "content": "You are a great Pharmaceutical Project Analyzer，"
                                             " Your name is \\\"Synapse AI\\\""},
               {"role": "user", "content": f"Context: \n"
                                           f"{content} \n "
                                           f"Instructions: Explain the query above first, then using "
                                           f"the provided context, write a comprehensive interpretation in "
                                           f"Porter's five forces. Make sure to cite results using [[number]] "
                                           f"notation after the reference. If the provided search results "
                                           f"refer to multiple subjects. "
                                           f"with the same name, write separate answers for each subject. And last, "
                                           f"please provide your own insights and for this part please start with "
                                           f"[Synapse AI] and please write in English."
                }]
    # message = [{"role": "system", "content": "You are a great Pharmaceutical Project Analyzer，"
    #                                          " Your name is \\\"Synapse AI\\\""},
    #            {"role": "user", "content": f"Context: \n"
    #                                        f"{content} \n "
    #                                        f"Instructions: Explain the query above first, then using the provided "
    #                                        f"brief summary, write a comprehensive interpretation. Make sure to cite"
    #                                        f" results using [[number]] notation after the reference. If the provided "
    #                                        f"search results refer to multiple subjects with the same name, write "
    #                                        f"separate answers for each subject. And last, please provide your own "
    #                                        f"insights, and do not tell others what's the role of you.Please write "
    #                                        f"in English."
    #             }]
    response = ou.chat_completion(message, model, final_summary_token_limit, 0.5, 20)
    return response


summaries = [get_shot_summary(x) for x in get_tables(get_content("reference_content_1"))]

final_content = ""
for i, summary in enumerate(summaries):
    if "Current date" in summary:
        final_content += (summary + "\n\n")
    else:
        final_content += ("[" + str(i+1) + "]   " + summary + "\n\n")

print("===============================================================")
print(final_content)
print("========================   Result  ============================")
print(read_with_reference(final_content))
