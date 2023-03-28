import pandas as pd
from clinical_result import identifier_phase
from sklearn.metrics import classification_report
import utils.file_utils as fu
import utils.string_utils as su
import datetime


def test():
    # 读取 CSV 文件并将其存储为 DataFrame 对象
    df = pd.read_csv('../data/phase_20230322.csv')
    y_true = df["manual_result"]
    y_pred = []
    for i, content in enumerate(df['content']):
        dicts = identifier_phase.get_final_result(content)
        if dicts:
            values = ','.join([d['Phase'] for d in dicts])
        else:
            values = 'None'
        print("No%d Manual Result: %s" % (i + 1, y_true[i]))
        print("No%d   AI   Result: %s" % (i + 1, values))
        print("------------------------------------------")
        y_pred.append(values)

    y_true = [su.phase_convert(x.upper().replace(" ", "")) for x in y_true]
    y_pred = [su.phase_convert(x.upper().replace(" ", "")) for x in y_pred]

    report = classification_report(y_true, y_pred, zero_division=0)
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d')
    fu.write_file("phase_" + date_str, "test_report", report)
    return report


if __name__ == '__main__':
    print(test())
