import re, csv, sys, subprocess, os, glob, shutil
import pandas as pd
from utils.fileUtils import read_txt
from utils.decompose_log import decompose_detections

REG_PTR = re.compile('Processing file')
REG_PTR_ORION = re.compile('Running')


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
                        
def detect_bugs(lib, iteration, release, tool):

    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    else:
        target_data = read_txt('data/tf_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')

    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/code-{tool}/fewshot/output/{lib}_demo/{iteration}/{release}/{release}.txt"
    output_dir = f"/media/nimashiri/DATA/testing_results/tosem/code-{tool}/fewshot/output"
    log_data_latest = read_txt(_path_to_logs_old)
    log_decomposed = decompose_detections(log_data_latest)
    
    try:    
        for idx, row in ground_truth.iterrows():
            for j, log in enumerate(log_decomposed):
                print(f'Running {lib}:{release}:{iteration} ground truth record: {idx}/{len(ground_truth)} // Log record {j}/{len(log_decomposed)}')
                if "Processing file" in log[0]:
                    api_name = log[0].split('/')[-2]
                    
                    if api_name in target_data:
                        if '.py' in api_name:
                            api_name = api_name.replace('.py', '')
                            
                        log_merged = ''.join(log)
                        pattern = re.compile(row['Log Rule'])
                        match = pattern.search(log_merged)
                        if match and row['Version'] == release:
                            output = [tool, lib, iteration, row['Version'], release, api_name, row['Log Message'], log_merged]
                                
                            with open(f"{output_dir}/detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                                write = csv.writer(file)
                                write.writerow(output)
                    else:
                        print('Not in target data!')
    except Exception as e:
        print(e)


                        
def main():
    # lib = sys.argv[1]
    # iteration = sys.argv[2]
    # release = sys.argv[3]
    # env_name = sys.argv[4]
    # task = sys.argv[5]
    
    lib = 'tf'
    iteration = 1
    release = '2.11.0'
    env_name = 'tf_2.11.0'
    task = 'detect'
    
    if task == 'dependency':
        insert_dependency(lib, iteration, release, env_name, 'atlasfuzz')
    # insert_dependency('tf', 1, '2.11.0', 'tf_2.11.0', 'atlasfuzz')
    elif task == 'capture':
        capture_output(lib, iteration, release, env_name, 'atlasfuzz')
    else:
        for lib in ['torch', 'tf']:
            for i in range(1, 2):
                
                if lib == 'tf':
                    releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
                else:
                    releases = ['2.0.0', '2.0.1', '2.1.0']
                for release in releases:    
                    detect_bugs(lib, i, release, 'atlasfuzz')


if __name__ == '__main__':
    main()