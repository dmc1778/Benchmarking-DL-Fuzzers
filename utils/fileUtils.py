import csv, os
import pandas as pd


def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def find_apis(x, target_data):
    flag = False
    for api in x:
        flag = True
    return flag

def list_python_files(directory):
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

def load_csv(fileName):
    return pd.read_csv(f'issues/{fileName}.csv', sep=',')

def write_to_csv(dirName,fileName, data):
    with open(f"./{dirName}/{fileName}.csv", "a", newline="\n",) as fd:
        writer_object = csv.writer(fd)
        writer_object.writerow(data)