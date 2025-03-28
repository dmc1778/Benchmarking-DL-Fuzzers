import csv, os, sys, json
import pandas as pd

def load_json(data_path):
    with open(data_path) as json_file:
        data = json.load(json_file)
    return data

def postprocess_test_statistics(df, tool_name, libname, release):
    x = df[(df['Library'] == libname ) & (df['Release'] == release)]
    
    x = x.groupby(['Library','Release']).mean(numeric_only=True)
    x = x.iloc[0].values.tolist()
    x.insert(0, libname)
    x.insert(1, release)
    return x    

def read_timestamps_from_file(file_path: str, libname: str):
    timestamps = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        if libname == 'torch':
                            ts = float(line)
                        else:
                            ts = float(line.split(' ')[0])
                        timestamps.append(ts)
                    except ValueError:
                        print(f"Warning: Could not convert line to float: '{line}'")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    return timestamps

def read_txt(_path):
    with open(_path, "r", encoding="utf-8", errors="ignore") as f:
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

def write_to_csv(fileName, data):
    with open(f"{fileName}.csv", "a", newline="\n",) as fd:
        writer_object = csv.writer(fd)
        writer_object.writerow(data)
        
def write_to_csvV2(data, parent, toolname, venue):
    if not os.path.exists(f"/home/nimashiri/Benchmarking-DL-Fuzzers/statistics/{venue}/{parent}/"):
        os.makedirs(f"/home/nimashiri/Benchmarking-DL-Fuzzers/statistics/{venue}/{parent}/")
    with open(f"/home/nimashiri/Benchmarking-DL-Fuzzers/statistics/{venue}/{parent}/{toolname}_1.csv", 'a', encoding="utf-8", newline='\n') as file_writer:
        write = csv.writer(file_writer)
        write.writerow(data)
