import openai
import pandas as pd
from tabulate import tabulate
import xmindparser
import openai_key

openai.api_key = openai_key.api_key

# Author : Ye Zhongkai

max_token = 500
case_step = 5
model = 'gpt-3.5-turbo'

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
                   {"role": "user", "content": f"Markdown table: \n {markdown} \n\n please write the software "
                                               f"test cases in Chinese, and the format should be "
                                               f"[Row Number] [Test cases title] \n Test Steps: [Test Steps] \n"
                                               f"Expected Result: [Expected Result],  "
                                               f"and remember if test steps are more than one line, "
                                               f"please put them into multiple lines, each test "
                                               f"case should less than 150 words, Test cases title should start with "
                                               f"previous [column value], if there are multiple previous columns, "
                                               f"and remember write in Chinese also remember each line in markdown "
                                               f"should mapping to one test case."
                                               f"For example: if one column is |1|药物检索|药物|根据药物id检索| | | | | |, "
                                               f"then the test should be like"
                                               f"[用例1] [药物检索-药物] 页面中实现检索当前机构以及子机构关联的研发状态，聚合药物id \n"
                                               f"测试步骤：\n 1) 输入机构id \n 2) 从下来选项中选择一个母公司 \n 3) 点击检索 \n"
                                               f"期望结果：\n 药物检索列表能够正确返回药物结果 "
                                               f"Another example, if another is |2|药物检索|药物类型|索引新增字段|DRUG_TYPE| | | | |"
                                               f"then the test should be like"
                                               f"[用例2] [药物检索-药物类型-索引新增字段] 在药物检索中判断检索字段 DRUG_TYPE 是否生效 \n"
                                               f"测试步骤：\n 1) 进入药物高级检索页面 \n 2) 选择 DRUG_TYPE 中其中一个 \n 3) 点击检索 \n"
                                               f"期望结果：\n 药物检索列表能够正确返回药物结果 "
                    }]

        response = openai.ChatCompletion.create(
            model=model,
            max_tokens=1500,
            messages=message,
            temperature=0.2
        )

        answer = response["choices"][0]["message"]["content"].strip()
        print(answer)


xls2markdown(xmind2xls(file_name))
