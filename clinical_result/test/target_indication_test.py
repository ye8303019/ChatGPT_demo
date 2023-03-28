import pandas as pd
from clinical_result import target_indication
from sklearn.metrics import classification_report
import utils.file_utils as fu
import datetime


def test():
    # 读取 CSV 文件并将其存储为 DataFrame 对象
    df = pd.read_csv('../data/target_indication_20230322.csv')
    y_true = df["manual_result"]
    y_pred = []
    for i, content in enumerate(df['content']):
        dicts = target_indication.get_final_result(content)
        values = ','.join([d['Target Indication'] for d in dicts])
        print("No%d Manual Result: %s" % (i + 1, y_true[i]))
        if not values:
            values = "None"
        print("No%d   AI   Result: %s" % (i + 1, values))
        print("------------------------------------------")
        y_pred.append(values)

    report = classification_report([x.upper() for x in y_true], [x.upper() for x in y_pred], zero_division=0)
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d')
    fu.write_file("target_indication_" + date_str, "test_report", report)
    return report


if __name__ == '__main__':
    print(test())
