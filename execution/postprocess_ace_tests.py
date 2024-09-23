import re, csv, sys, subprocess, os, glob, shutil
# sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
# from utils.log_similarity import calculate_similarity
import sys
import pandas as pd


REG_PTR = re.compile('Processing file')
REG_PTR_ORION = re.compile('Running')

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

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def capture_output(lib, iteration,_version, env_name, tool) -> None:
    iteration = iteration - 1
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/Tester/src/output/output_{lib}_{iteration}/{_version}"
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')

    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for api_ in directories:
        current_api = os.path.join(_path_to_logs_old, api_)
        oracles_ = os.listdir(current_api)
        for oracle in ['crash', 'non_crash']:
            current_oracle = os.path.join(current_api, oracle)
            current_tests = os.listdir(current_oracle)
            if current_tests:
                for test_file in current_tests:
                    current_test_path = os.path.join(current_oracle, test_file)
                    if current_test_path.endswith('.py'):
                        shell_command = ["post_processing/capture_ace_log.sh",lib, _version, tool, env_name, current_test_path, str(iteration)]
                        subprocess.call(shell_command,shell=False)

def save_ace_logs(lib, iteration,_version, tool):
    iteration_ = iteration - 1
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    else:
        target_data = read_txt('data/tf_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/Tester/src/output/output_{lib}_{iteration_}/{_version}/{_version}.txt"
    output_path  = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/Tester/src/output"
    log_data_latest = read_txt(_path_to_logs_old)
    log_decomposed = decompose_detections(log_data_latest)
    
    # log_message_column = ground_truth['Log Message']
    
    for idx, row in ground_truth.iterrows():
        for log in log_decomposed:
            if "Processing file" in log[0]:
                api_name = log[0].split('/')[-3]
                print(api_name)
                if row['Buggy API'] == api_name:
                    if '.py' in api_name:
                        api_name = api_name.replace('.py', '')
                    decom_ = ''.join(log[-2:])
                    # score_ = calculate_similarity(ground_truth.iloc[idx, 4], decom_)
                    flag = row['Impact'] in decom_
                    if flag and row['Version'] == _version:
                        output = [tool, iteration_, row['Version'], _version, api_name, row['Log Message'], decom_]
                        
                        with open(f"{output_path}/{lib}_detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                            write = csv.writer(file)
                            write.writerow(output)
                    else:
                        print('No detection')

def main():
    # lib = sys.argv[1]
    # iteration = int(sys.argv[2])
    # release = sys.argv[3]
    # env_name = sys.argv[4]

    #save_ace_logs(lib, iteration, release, env_name, 'ACETest')
    lib = 'torch'
    for i in range(1, 5):
        if lib == 'tf':
            releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
        else:
            releases = ['2.0.0', '2.0.1', '2.1.0']
        for release in releases:
            save_ace_logs(lib, i, release, 'ACETest')

if __name__ == '__main__':
    main()