import openai
import utils.openai_utils as ou
import pandas as pd
from tabulate import tabulate
import xmindparser

import main
import openai_key

openai.api_key = openai_key.api_key

# Author : Ye Zhongkai

max_token = 1500
case_step = 5
model = main.OPENAI_MODEL

# Drug Search Upgrade.xmind, Synapse PLG 2.0.xmind,专利1.2.xmind,多靶点遗留.xmind,Dashboard 优化.xmind
file_name = 'Synapse PLG 2.0.xmind'


def max_level(tree_dict, current_level=0, max_level_number=0):
    if tree_dict:
        current_level += 1
        if current_level > max_level_number:
            max_level_number = current_level
        for tree_dict_item in tree_dict:
            if "topics" in tree_dict_item:
                max_level_number = max_level(tree_dict_item["topics"], current_level, max_level_number)
    return max_level_number


def topic2column(df, tree_dict, titles, max_level_number):
    if tree_dict:
        for tree_dict_item in tree_dict:
            current_titles = titles.copy()
            current_titles.append(tree_dict_item["title"])
            if "topics" in tree_dict_item:
                topic2column(df, tree_dict_item["topics"], current_titles, max_level_number)
            else:
                if len(current_titles) < max_level_number:
                    for i in range(0, max_level_number - len(current_titles)):
                        current_titles.append(" ")
                df.loc[len(df)] = current_titles


def xmind2xls(xmind_file):
    # 读取 Xmind 文件
    tree = xmindparser.xmind_to_dict(xmind_file)

    # 获取第一个 Topic 的 title 用作 excel 文件名称
    xls_file_name = tree[0]["topic"]["title"] + '.xlsx'

    max_level_number = max_level(tree[0]["topic"]["topics"])

    print("xmind max level is %d" % max_level_number)

    cols = []
    for col in range(max_level_number):
        cols.append("level %d" % col)

    # 构造一个空的 df
    df = pd.DataFrame(columns=cols)

    # 遍历 tree，每次遇到根节点，则往 excel 中增加一行
    titles = []
    topic2column(df, tree[0]["topic"]["topics"], titles, max_level_number)

    # 将 DataFrame 对象写入 Excel 文件
    df.to_excel(xls_file_name, index=False)
    return xls_file_name


def xls2markdown(xls_file):
    df = pd.read_excel(xls_file, header=None)
    num_rows = df.shape[0]

    for row in range(1, num_rows, case_step):
        if (row + case_step) < num_rows:
            df_chunk = df.iloc[row:row + case_step]
        else:
            df_chunk = df.iloc[row:num_rows]

        markdown = tabulate(df_chunk, headers='keys', tablefmt='pipe')

        # Print the Markdown output
        print(markdown)

        message = [{"role": "system", "content": "Now you are a excellent software quality assurance "
                                                 "people, you are good at writing test cases through markdown table"},
                   {"role": "user", "content": "I will give you a context in markdown format, and you will "
                                               "write the test cases, do you understand?"},
                   {"role": "assistant", "content": "Yes, I understand. Please provide me with the context in "
                                                    "Markdown format, and I will write the test cases for you."},
                   {"role": "user", "content": f"Markdown table: \n"
                                               f" {markdown} \n\n "
                                               f"Please write the software "
                                               f"test cases in Chinese, and the reply format should be:\n "
                                               f"[Row Number] [Test cases title] XXXXXXX \n "
                                               f"Test Steps: [Test Steps] \n"
                                               f"Expected Result: [Expected Result] \n"
                                               f"Priority: [Priority] \n\n"
                                               f"Rules:"
                                               f"1. If test steps are more than one line, "
                                               f"please put them into multiple lines \n"
                                               f"2. each test case should less than 150 words \n"
                                               f"3. Test cases title should start with previous [column value], "
                                               f"if there are multiple previous columns, use '-' to separate them  \n"
                                               f"4. Answer in Chinese also \n"
                                               f"5. Each line of the markdown table must be one test case. \n"
                                               f"6. Each 'Test Steps' item must have an 'Expected Result' item to be "
                                               f"mapping to \n "
                                               f"7. 'Priority' only could be '高', '中', '低' \n"
                                               f"8. If the cause is 'search', 'analysis', 'table list', 'data', "
                                               f"'security' "
                                               f"related, the priority should be '高' \n "
                                               f"9. If the case is 'UIUX', 'frontend', 'basic logic' related, "
                                               f"the priority should be '低' \n "
                                               f"10. Except rule 8 and rule 9, for others, the priority should be '中' "
                                               f"\n\n "
                                               f"Examples: \n"
                                               f"if a row of the markdown table is: \n"
                                               f" |1|竞争格局|适应症|临床试验的国家/地区分布| | | | | |, "
                                               f"Test case answer:"
                                               f"[用例1] [药物检索-药物] 临床试验的国家/地区分布 - 检查图表显示正确 \n"
                                               f"测试步骤：\n "
                                               f"1) 检查总览tab，单靶点EGFR的临床试验的国家/地区分布以及显示 \n "
                                               f"2) 检查作用机制tab，单靶点EGFR，EGFR拮抗剂的临床试验的国家/地区分布以及显示 \n "
                                               f"3) 检查多靶点PD1+LAG3 的临床试验的国家/地区分布以及显示 \n"
                                               f"期望结果：\n "
                                               f"1)显示国家/地区的临床分布并且检查美国的临床数量和临床检索 EGFR，过滤美国后，需要数量一致\n"
                                               f"2)显示国家/地区的临床分布数据并且检查美国的临床数量和临床检索 EGFR，过滤美国后，需要数量一致\n"
                                               f"3)显示国家/地区临床分布数据并且检查美国的临床数量和临床检索 PD1+LAG3，过滤美国后，需要数量一致 \n"
                                               f"优先级：\n"
                                               f"高\n\n"
                                               f"Another example, if a row of the markdown table is:\n"
                                               f"|2|公司详情页|专利|公司专利分析|Total patent docs| | | | |"
                                               f"Test case answer: \n"
                                               f"[用例2] [公司详情页-专利-公司专利分析] atents标题后面info中的“Total patent "
                                               f"docs”在勾选与不勾选Include subsidiary时显示不一样 \n "
                                               f"测试步骤：\n "
                                               f"1) 进入Google LLC详情页+ 语言为英文 \n "
                                               f"2) hover在Patents后面的info \n "
                                               f"3) 取消勾选Include subsidiary + 语言切换为中文 \n"
                                               f"期望结果：\n "
                                               f"1)Data Snapshot 后面的 Include subsidiary 默认勾选\n"
                                               f"2)展示：This patent count is grouped by 'one doc per application'. "
                                               f"Total patent docs: 163K\n "
                                               f"3)专利总数按照APNO方式折叠，总专利文档数：128K\n"
                                               f"优先级：\n"
                                               f"高\n\n"
                    }]

        response = ou.chat_completion(message, model, max_token, 0.8, 60)
        print(response)


xls2markdown(xmind2xls(file_name))
