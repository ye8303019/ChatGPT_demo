import token_calculator_demo.token_calculator as tc
import re
import time
import sys
import threading
import main
import utils.openai_utils as ou

# Author : Ye Zhongkai
max_token = 1000
model = main.OPENAI_CHAT_MODEL


# Remove new lines from the text
def remove_newlines(series):
    series = series.replace('\n', ' ')
    series = series.replace('\\n', ' ')
    series = series.replace('  ', ' ')
    series = series.replace('  ', ' ')
    return series


def dict2markdown(my_dict):
    # Get the header and data rows
    header = "| Argument Role | Argument Content |\n|:-----|:----------------|"
    rows = ["| " + key + " | " + value + " |" for key, value in my_dict.items()]
    # Join the header and data rows
    table = header + "\n" + "\n".join(rows)
    return table


def get_news_content(file_name, token_threshold):
    file_contents = []
    # Open the file in read mode
    with open(file_name, 'r', encoding='utf-8') as file:
        # Read the file content and store it in a variable
        file_content = file.read()
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


def format_answer(answer):
    data_list = []
    if "Argument Role" in answer:
        if "Event" in answer:
            # Split the table into lines
            lines = answer.strip().split("\n")
            rows = []
            for line in lines:
                if "[Event" in line:
                    continue
                elif "Argument Role" in line and len(rows) > 0:
                    rows = rows[2:]
                    argument_roles = []
                    argument_contents = []
                    for x in rows:
                        if x and x != "":
                            argument_roles.append(x.split("|")[1].strip())
                            argument_contents.append(x.split("|")[2].strip())
                    # Create a dictionary from the argument roles and argument contents
                    data_list.append(dict(zip(argument_roles, argument_contents)))
                    rows.clear()
                    rows.append(line)
                else:
                    rows.append(line)
        else:
            # Split the table into lines
            lines = answer.strip().split("\n")

            # Split the header and data rows
            rows = lines[2:]
            argument_roles = []
            argument_contents = []
            for x in rows:
                if x and x != "":
                    key = x.split("|")[1].strip()
                    if key in argument_roles:
                        data_list.append(dict(zip(argument_roles, argument_contents)))
                        argument_roles.clear()
                        argument_contents.clear()
                    argument_roles.append(key)
                    argument_contents.append(x.split("|")[2].strip())

            # Create a dictionary from the argument roles and argument contents
            data_list.append(dict(zip(argument_roles, argument_contents)))
    return data_list


def news_ee(news_content):
    message = [{"role": "system", "content": "Now you are a great data content guy, you good at extract life "
                                             "science related entity, event, relationships from a sentence "
                                             "or paragraph or article"},
               {"role": "user", "content": "Now I will give you a definition about my event type which wants "
                                           "you to extract them from the content later, do you understand?"},
               {"role": "assistant", "content": "Yes, please provide me with the definition of your event type, "
                                                "and I'll do my best to extract them from the content."},
               {"role": "user", "content": f"The list of argument roles corresponding to the event type "
                                           f"[Drug : R&D status] is ['Company', 'Drug', 'Country/Location', "
                                           f"'Date', 'Study Phase/Approval'], and i will give you a sentence "
                                           f"or paragraph or article, please extract the event arguments according "
                                           f"to the argument roles, and return them in the form of a table."
                                           f"If no argument role has a corresponding argument content, "
                                           f"the argument content returns 'None'.  Remember do not merge multiple "
                                           f"events into one markdown table. "
                                           f"Here are 4 examples:\n"
                                           f"   1) In the paragraph below:\n"
                                           f"   'AB Science has received approval from the U.S. Food and Drug "
                                           f"Administration (FDA) to initiate the confirmatory Phase 3 study with "
                                           f"masitinib in the treatment of progressive multiple sclerosis. Paris, "
                                           f"December 29 2022, 6pm CET AB Science SA (Euronext - FR0010557264 - AB) "
                                           f"announced today that its Phase III clinical trial (AB20009) in progressive "
                                           f"forms of multiple sclerosis has been approved by the US Food and Drug "
                                           f"Administration (FDA).This decision follows authorizations received from "
                                           f"several European countries, including the French Agency (ANSM) This "
                                           f"approval to initiate a confirmatory study in neurology is the third "
                                           f"obtained from the FDA after studies in Amyotrophic Lateral Sclerosis "
                                           f"(AB19001) and Alzheimer's disease (AB21004).' Then the table of "
                                           f"the arguments should be:"
                                           f"| Argument Role | Argument Content | \n"
                                           f"|:-----|:----------------|\n"
                                           f"| Company | AB Science |\n"
                                           f"| Drug | Masitinib  |\n"
                                           f"| Disease | Progressive multiple sclerosis  |\n"
                                           f"| Country/Location | US |\n"
                                           f"| Date | 2022-12-29 |\n"
                                           f"| Study Phase/Approved | Phase 3 |\n"
                                           f"   3) In the paragraph below: \n"
                                           f"'Reata Pharma Drug Wins First FDA Nod in Ultra-Rare Neuromuscular Disorder "
                                           f"Skyclarys, a Reata Pharmaceuticals drug, is now approved for treating the "
                                           f"rare neuromuscular disorder Friedreich’s ataxia. The decision makes the "
                                           f"capsule the first therapy for a disease that’s rarer than either Duchenne "
                                           f"muscular dystrophy or spinal muscular atrophy. Post a comment / Feb 28, "
                                           f"2023 at 7:38 PM Friedrich’s ataxia, an ultra-rare disease characterized by "
                                           f"progressively worsening muscle function that ultimately leads to death, "
                                           f"now has its first FDA-approved therapy. The regulator has given the green "
                                           f"light to a Reata Pharmaceuticals drug that addresses a cellular component "
                                           f"impaired by the inherited disorder. The approval announced Tuesday evening "
                                           f"covers the treatment of adults as well as adolescents 16 and older. The "
                                           f"recommended dose is three capsules taken once daily. Known in development "
                                           f"as omeveloxolone, Plano, Texas-based Reata will commercialize its new drug "
                                           f"as “Skyclarys.” “It is gratifying to have received this approval on Rare "
                                           f"Disease Day,” Reata CEO Warren Huff said, speaking during a Tuesday "
                                           f"evening conference call. “That "
                                           f"underscores the progress that has been made by many patient groups, "
                                           f"researchers, investigators, regulators, and others in the development of "
                                           f"therapeutics for rare diseases.” '\n"
                                           f"Then the table of the arguments should be:"
                                           f"| Argument Role | Argument Content | \n"
                                           f"|:-----|:----------------| \n"
                                           f"| Company | Reata Pharma | \n"
                                           f"| Drug | Skyclarys | \n"
                                           f"| Disease | Friedrich’s ataxia | \n"
                                           f"| Country/Location | US | \n"
                                           f"| Date | 2023-2-28 | \n"
                                           f"| Study Phase/Approved | Approved | \n"
                                           f" 4) In the paragraph below:"
                                           f"for example: '近日，默沙东披露了PCSK9抑制剂MK-0616治疗成人高胆固醇血症患者的 2b 期临床试验的积极结果。"
                                           f"结果显示，4个剂量组（6mg，12mg，18mg，30mg）治疗8周后LDL-C的降低幅度从41.2%至 60.9 %，"
                                           f"且临床耐受性表现良好。基于此，默沙东计划于今年下半年启动 III 期关键研究。 NN-6435（NNC0385-0434）"
                                           f"是另一种小分子多肽PCSK9抑制剂，由诺和诺德开发，目前正在全球开展1期和2期临床试验。  "
                                           f"3月9日，中国国家药监局药品审评中心（CDE）官网公示，阿斯利康（AstraZeneca）递交了1类新药AZD9592的临床试验"
                                           f"申请，并获得受理。根据阿斯利康公开资料，AZD9592是一款利用其内部专有的抗体偶联药物（ADC）技术研发的新产品"
                                           f"，以EGFR-cMET为靶点，正在海外开展1期临床研究"
                                           f"then the table of the arguments should be:"
                                           f"[Event 1] \n"
                                           f"| Argument Role | Argument Content | \n"
                                           f"|:-----|:----------------| \n"
                                           f"| Company | 默沙东 | \n"
                                           f"| Drug | MK-0616 | \n"
                                           f"| Disease | 成人高胆固醇血症 | \n"
                                           f"| Country/Location | None | \n"
                                           f"| Date | None | \n"
                                           f"| Study Phase/Approved | Phase 2b | \n"
                                           f""
                                           f"[Event 2] \n"
                                           f"| Argument Role | Argument Content | \n"
                                           f"|:-----|:----------------| \n"
                                           f"| Company | 诺和诺德 | \n"
                                           f"| Drug | NN-6435（NNC0385-0434） | \n"
                                           f"| Disease | Friedrich’s ataxia | \n"
                                           f"| Country/Location | 全球 | \n"
                                           f"| Date | None | \n"
                                           f"| Study Phase/Approved | Phase1 Phase2 | \n"
                                           f""
                                           f"[Event 3] \n"
                                           f"| Argument Role | Argument Content | \n"
                                           f"|:-----|:----------------| \n"
                                           f"| Company | 阿斯利康 | \n"
                                           f"| Drug | AZD9592 | \n"
                                           f"| Disease | 实体瘤 | \n"
                                           f"| Country/Location | 中国 | \n"
                                           f"| Date | 2023-03-09 | \n"
                                           f"| Study Phase/Approved | 临床试验申请 | \n\n"
                                           f"Notice: DO NOT MERGE THE DRUG OR DISEASE INTO ONE EVENT, SEPARATE THEM "
                                           f"INTO MULTIPLE EVENTS ! \n\n "
                                           f"Now, please use this rule to extract the event and it's arguments from  \n"
                                           f"the content below: \n"
                                           f"{news_content}"
                }]

    return ou.chat_completion(message, model, max_token, 0.2, 50)


stop_thread = False


def loading():
    global stop_thread
    loading_count = 0
    while not stop_thread:
        time.sleep(0.05)
        dots = ""
        for j in range((loading_count % 3) + 1):
            dots += ". "
        sys.stdout.write("\rLoading %s" % dots)
        sys.stdout.flush()
        loading_count += 1


print("=========  正在将内容进行拆分/组合/调用/抽取   ===========")

loading_thread = threading.Thread(target=loading)
loading_thread.start()

# news_content_1, news_content_2
file_contents = get_news_content('news_content_7', 1300)
results = [news_ee(x) for x in file_contents]

count = 0
stop_thread = True
loading_thread.join()
print("")
print("")
print("=================  Final Results   =================")
for answer in results:
    formatted_answer = format_answer(answer)
    for i, data in enumerate(formatted_answer):
        if data and 'Company' in data and data['Company'] != 'None' and 'Drug' in data and data['Drug'] != 'None':
            count += 1
            print("")
            print("**************** 事件 %d  ***************" % count)
            print("")
            print(dict2markdown(data))
            print("")
            print("****************************************")


if count == 0:
    print("*************************************************")
    print("No Event")

stop_thread = True
loading_thread.join()

print("")
print("\n================ 抽取结束 ==========================")

# print(format_answer(""))
