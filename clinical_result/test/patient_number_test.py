import pandas as pd
from clinical_result import patient_number
from sklearn.metrics import classification_report
import utils.file_utils as fu
import utils.string_utils as su
import datetime


def test():
    # 读取 CSV 文件并将其存储为 DataFrame 对象
    df = pd.read_csv('../data/patient_number_20230322.csv')
    y_true = df["manual_result"]
    y_pred = []
    for i, content in enumerate(df['content']):
        values = ""
        dicts = patient_number.get_final_result(content)
        if dicts:
            for j, d in enumerate(dicts):
                if d['Overall Enrollment'] != 'None':
                    if j == (len(dicts) - 1):
                        values += d['Overall Enrollment']
                    else:
                        values += d['Overall Enrollment'] + ","
        else:
            values = 'None'
        print("No%d Manual Result: %s" % (i + 1, y_true[i]))
        print("No%d   AI   Result: %s" % (i + 1, values))
        print("------------------------------------------")
        y_pred.append(values)

    y_true = [x.upper().replace(" ", "") for x in y_true]
    y_pred = [x.upper().replace(" ", "") for x in y_pred]

    report = classification_report(y_true, y_pred, zero_division=0)
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d')
    fu.write_file("phase_" + date_str, "test_report", report)
    return report


if __name__ == '__main__':
    print(test())
