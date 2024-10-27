import re, csv, sys, subprocess, os, glob, shutil
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
# from utils.log_similarity import calculate_similarity
from utils.decompose_log import decompose_detections
import pandas as pd
from utils.fileUtils import read_txt, list_python_files, find_apis

def capture_output(lib, iteration, release, env_name, tool) -> None:
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{iteration}/{release}/expr"
    
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')
    directories = ['output-0']
    for dir_ in directories:
        current_dir = os.path.join(_path_to_logs_old, dir_)
        all_pairs = os.listdir(current_dir)
        for pair in all_pairs:
            current_oracle = os.path.join(current_dir, pair)
            if "+" not in current_oracle:
                continue
            current_files = list_python_files(current_oracle)
            for api in current_files:
                api_split = api.split('/')
                extracted_item = next((item for item in api_split if '+' in item), None)
                apis_extracted = extracted_item.split('+')
                x = []
                for item in apis_extracted:
                    if 'tf.' in item or 'torch.' in item:
                        x.append(item)
                flag = find_apis(x, target_data)
                if flag and re.findall(r'(\bbug\b|\bneq\b)',  api):
                    shell_command = ["post_processing/capture_log_deeprel.sh",lib, release, tool, env_name, api, str(iteration)]
                    subprocess.call(shell_command,shell=False)
                    
def detect_bugs(lib, iteration,_version, tool) -> None:
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{iteration}/{_version}/expr/{_version}.txt"
    output_path  = f"/media/nimashiri/DATA/testing_results/tosem"
    
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')
        
    ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
    
    log_data_latest = read_txt(_path_to_logs_old)
    log_decomposed = decompose_detections(log_data_latest)
    
    for idx, row in ground_truth.iterrows():
        for j, log in enumerate(log_decomposed):
            print(f'Running {lib}:{_version}:{iteration} ground truth record: {idx}/{len(ground_truth)} // Log record {j}/{len(log_decomposed)}')
            if "Processing file" in log[0]:
                api_name = log[0].split('/')
                extracted_item = next((item for item in api_name if '+' in item), None)
                if "+" not in extracted_item:
                    continue
                apis_extracted = extracted_item.split('+')
                api_name = apis_extracted[0]
                if api_name not in target_data:
                    continue
                if row['Buggy API'] == api_name:
                    if '.py' in api_name:
                        api_name = api_name.replace('.py', '')
                    log_merged = ''.join(log)
                    #flag = row['Impact'] in decom_
                    # score = calculate_similarity(row['Log Message'], decom_)
                    pattern = re.compile(row['Log Rule'])
                    match = pattern.search(log_merged)
                    if match and row['Version'] == _version:
                        output = [tool, lib, iteration,row['Issue'], row['Version'], _version, api_name, row['Log Message'], log_merged]
                        with open(f"{output_path}/detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                            write = csv.writer(file)
                            write.writerow(output)
                        break
                else:
                    print('Not among target APIs.')
    
if __name__ == '__main__':
    # lib = sys.argv[1]
    # iteration = sys.argv[2]
    # release = sys.argv[3]
    # env_name = sys.argv[4]

    for lib in ['torch', 'tf']:
        for i in range(1, 5):
            if lib == 'tf':
                releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
            else:
                releases = ['2.0.0', '2.0.1', '2.1.0']
            for release in releases:
                detect_bugs(lib, i, release, 'DeepRel')