import os


def write_file(file_name, file_path, content):
    if file_path and not file_path.endswith('/'):
        file_path += '/'

    # 判断文件是否存在
    if os.path.isfile(file_path+file_name):
        # 文件存在，添加递增序号
        i = 1
        while True:
            # 构造新的文件名
            if os.path.splitext(file_name)[1]:
                new_filename = f"{os.path.splitext(file_name)[0]}({i}){os.path.splitext(file_name)[1]}"
            else:
                new_filename = f"{os.path.splitext(file_name)[0]}({i})"
            # 判断新的文件名是否存在
            if os.path.isfile(file_path+new_filename):
                # 文件存在，递增序号
                i += 1
            else:
                # 文件不存在，保存文件并跳出循环
                file_name = new_filename
                break

    with open(file_path+file_name, 'w', encoding='utf-8') as f:
        f.write(content)


def get_content(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        # Read the file content and store it in a variable
        file_content = file.read()
    return file_content
