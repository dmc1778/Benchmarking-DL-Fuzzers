import re, csv, sys, subprocess, os, glob, shutil

REG_PTR = re.compile('Processing file')
REG_PTR_ORION = re.compile('Running')

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def decompose_detections(splitted_lines):
    super_temp = []
    j = 0
    indices = []
    while j < len(splitted_lines):
        if REG_PTR.search(splitted_lines[j]):
            indices.append(j)
        if REG_PTR_ORION.search(splitted_lines[j]):
            indices.append(j)
        j += 1

    if len(indices) == 1:
        for i, item in enumerate(splitted_lines):
            if i != 0:
                super_temp.append(item)
        super_temp = [super_temp]
    else:
        i = 0
        j = 1
        while True:
            temp = [] 
            for row in range(indices[i], indices[j]):
                temp.append(splitted_lines[row])
            super_temp.append(temp)
            if j == len(indices)-1:
                temp = [] 
                for row in range(indices[j], len(splitted_lines)):
                    temp.append(splitted_lines[row])
                super_temp.append(temp)
                break
            i+= 1
            j+= 1

    return super_temp

def capture_output(lib, iteration, release, env_name, tool) -> None:
    
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/code-{tool}/fewshot/output/{lib}_demo/{iteration}/{release}"

    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')

    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for dir_ in directories:
        current_path = os.path.join(_path_to_logs_old, dir_)
        current_files = os.listdir(current_path)
        for file_ in current_files:
            current_file = os.path.join(current_path, file_)
            shell_command = ["post_processing/capture_log_fuzzgpt.sh",lib, release, tool, env_name, current_file, str(iteration)]
            subprocess.call(shell_command,shell=False)
    
def insert_dependency(lib, iteration,_version, env_name, tool):
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/code-{tool}/fewshot/output/{lib}_demo/{iteration}/{_version}/"
    
    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for dir_ in directories:
        print(dir_)
        current_target_dir = os.path.join(_path_to_logs_old, dir_)
        py_files = os.listdir(current_target_dir)
        for file_ in py_files:  
                code_path = os.path.join(current_target_dir, file_)
                if file_.endswith(".py"):
                    code_ = read_txt(code_path)
                    if lib == 'tf':
                        code_.insert(0, 'import tensorflow as tf')
                        code_.insert(1, 'import numpy as np')
                        code_.insert(2, 'import os')
                        # code_.insert(3, 'import matplotlib.pyplot as plt')
                    else:
                        code_.insert(0, 'import torch')
                        code_.insert(1, 'import torch as pt')
                        code_.insert(2, 'import numpy as np')
                        code_.insert(2, 'import os')
                        # code_.insert(3, 'import matplotlib.pyplot as plt')
                    with open(code_path, "w", encoding="utf-8", newline='\n') as out_file:
                        for line in code_:
                            out_file.write(line + "\n")
                        
def save_atlasfuzz_results(lib, tool, release):

    if lib == 'torch':
        target_data = read_txt('/home/nimashiri/torch_test_apis_1.txt')
    else:
        target_data = read_txt('/home/nimashiri/tf_test_apis_1.txt')


    log_data_old = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{release}/{release}.txt"
    output_dir = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{release}/"
    log_data_latest = read_txt(log_data_old)
    log_decomposed = decompose_detections(log_data_latest)
    for log in log_decomposed:
        if "Processing file" in log[0]:
            test_err_full = log[-5:]
            test_err_symp = log[-1]
            api_name = log[0].split('/')[-2]
            
            if api_name in target_data:
                if '.py' in api_name:
                    api_name = api_name.replace('.py', '')

                print(api_name)

                decom_ = ''.join(log)
                output = [tool, release, api_name, decom_]
                
                with open(f"{output_dir}{release}.csv", "a", encoding="utf-8", newline='\n') as file:
                    write = csv.writer(file)
                    write.writerow(output)
            else:
                print('Not in target data!')


                        
def main():
    lib = sys.argv[1]
    iteration = sys.argv[2]
    release = sys.argv[3]
    env_name = sys.argv[4]
    task = sys.argv[5]
    
    # lib = 'tf'
    # iteration = 1
    # release = '2.11.0'
    # env_name = 'tf_2.11.0'
    # task = 'capture'
    
    if task == 'dependency':
        insert_dependency(lib, iteration, release, env_name, 'atlasfuzz')
    # insert_dependency('tf', 1, '2.11.0', 'tf_2.11.0', 'atlasfuzz')
    elif task == 'capture':
        capture_output(lib, iteration, release, env_name, 'atlasfuzz')
    else:
        save_atlasfuzz_results(lib, iteration, release, env_name, 'atlasfuzz')


if __name__ == '__main__':
    main()