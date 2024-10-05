import re, csv, sys, subprocess, os, glob, shutil
import pandas as pd
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
from utils.decompose_log import decompose_detections
from utils.fileUtils import read_txt
REG_PTR = re.compile('Processing file')
REG_PTR_ORION = re.compile('Running')

def capture_output(lib, iteration,_version, env_name, tool) -> None:
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{iteration}/{_version}"
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')

    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for dir_ in directories:
        current_dir = os.path.join(_path_to_logs_old, dir_)
        oracles_ = os.listdir(current_dir)
        for oracle in ['potential-bug']:
            current_oracle = os.path.join(current_dir, oracle)
            current_apis = os.listdir(current_oracle)
            for api_dir in current_apis:
                api_under_test = os.path.join(current_oracle, api_dir)
                list_apis = os.listdir(api_under_test)
                for file in list_apis:
                    file_to_run = os.path.join(api_under_test, file)
                    if api_dir in target_data:
                        shell_command = ["execution/capture_log_freefuzz.sh",lib, _version, tool, env_name, dir_, oracle, api_dir, str(iteration), file_to_run]
                        subprocess.call(shell_command,shell=False)

def detect_bugs(lib, iteration,_version, tool):
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    else:
        target_data = read_txt('data/tf_apis.txt')
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{iteration}/{_version}/{_version}.txt"
    output_path  = f"/media/nimashiri/DATA/testing_results/tosem"
    log_data_latest = read_txt(_path_to_logs_old)
    log_decomposed = decompose_detections(log_data_latest)

    for idx, row in ground_truth.iterrows():
        for j, log in enumerate(log_decomposed):
            print(f'Running {lib}:{_version}:{iteration} ground truth record: {idx}/{len(ground_truth)} // Log record {j}/{len(log_decomposed)}')
            if "Processing file" in log[0]:
                    api_name = log[0].split('/')[-2]
                    if row['Buggy API'] == api_name:
                        if '.py' in api_name:
                            api_name = api_name.replace('.py', '')
                        log_merged = ''.join(log)
                        pattern = re.compile(row['Log Rule'])
                        match = pattern.search(log_merged)
                        if match and row['Version'] == _version:
                            output = [tool, lib, iteration, row['Issue'], row['Version'], _version, api_name, row['Log Message'], log_merged]
                            
                            with open(f"{output_path}/detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                                write = csv.writer(file)
                                write.writerow(output)
                            break
                        else:
                            print('No detection')

def main():
    # lib = sys.argv[1]
    # iteration = sys.argv[2]
    # release = sys.argv[3]
    # env_name = sys.argv[4]
    # capture_output(lib, iteration,release, env_name, 'FreeFuzz')
    # capture_output('torch', 1, '2.0.0', 'torch_2.0.0', 'FreeFuzz')
    for lib in ['torch','tf']:
        if lib == 'tf':
            releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
        else:
            releases = ['2.0.0', '2.0.1', '2.1.0']
        for release in releases:
            detect_bugs(lib, 1, release, 'FreeFuzz')

if __name__ == '__main__':
    main()