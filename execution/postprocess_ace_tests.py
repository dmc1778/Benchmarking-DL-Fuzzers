import re, csv, sys, subprocess, os, glob, shutil
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')

import sys
import pandas as pd
from utils.decompose_log import decompose_detections
from utils.fileUtils import read_txt

def capture_output(lib, iteration,_version, env_name, tool) -> None:
    iteration = iteration - 1
    _path_to_logs_old = f"/media/nimashiri/DATA/fuzzers/{tool}/Tester/src/output/output_{lib}_{iteration}/{_version}"
    if lib == 'torch':
        target_data = read_txt('data/torch_icse_data.txt')
    else:
        target_data = read_txt('data/tf_icse_data.txt')

    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for api_ in directories:
        current_api = os.path.join(_path_to_logs_old, api_)
        oracles_ = os.listdir(current_api)
        for oracle in ['invalid', 'crash', 'non_crash', ]:
            current_oracle = os.path.join(current_api, oracle)
            current_tests = os.listdir(current_oracle)
            if current_tests:
                for test_file in current_tests:
                    current_test_path = os.path.join(current_oracle, test_file)
                    if current_test_path.endswith('.py'):
                        shell_command = ["/home/nimashiri/Benchmarking-DL-Fuzzers/execution/capture_ace_log.sh",lib, _version, tool, env_name, current_test_path, str(iteration)]
                        subprocess.call(shell_command,shell=False)

def detect_bugs(lib, iteration,_version, tool):
    if lib == 'torch':
        target_data = read_txt('data/torch_icse_data.txt')
        ground_truth = pd.read_csv(f'data/checker_groundtruth.csv')
    else:
        target_data = read_txt('data/tf_icse_data.txt')
        ground_truth = pd.read_csv(f'data/checker_groundtruth.csv')
    
    _path_to_logs_old = f"/media/nimashiri/DATA/fuzzers/{tool}/Tester/src/output/output_{lib}_{iteration}/{_version}/{_version}.txt"
    output_path  = f"/media/nimashiri/DATA/testing_results/icse26"
    log_data_latest = read_txt(_path_to_logs_old)
    log_decomposed = decompose_detections(log_data_latest)
    
    # log_message_column = ground_truth['Log Message']
    
    for idx, row in ground_truth.iterrows():
        for log in log_decomposed:
            if "Processing file" in log[0]:
                try:
                    api_name = log[0].split('/')[-3]
                    print(api_name)
                    if api_name not in target_data:
                        continue
                    if row['Buggy API'] == api_name:
                        if '.py' in api_name:
                            api_name = api_name.replace('.py', '')
                        decom_ = ''.join(log[-2:])
                        # score_ = calculate_similarity(ground_truth.iloc[idx, 4], decom_)
                        flag = row['Log Rule'] in decom_
                        if flag:#and row['Version'] == _version:row['Version']
                            output = [tool, lib, iteration, row['Commit'], _version, api_name, row['Log Rule'], decom_]
                            with open(f"{output_path}/detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                                write = csv.writer(file)
                                write.writerow(output)
                            break
                        else:
                            print('No detection')
                except Exception as e:
                    print(e)

def main():
    # lib = sys.argv[1]
    # iteration = int(sys.argv[2])
    # release = sys.argv[3]
    # env_name = sys.argv[4]

    for lib in ['tf','torch']:
        for i in [0]:
            if lib == 'tf':
                releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0", "2.15.0"]
            else:
                releases = ['1.13.0' ,'2.0.0', '2.0.1', '2.1.0', '2.2.0']
            for release in releases:
                env_name = f"{lib}_{release}"
                detect_bugs(lib, i, release, 'ACETest')

if __name__ == '__main__':
    main()