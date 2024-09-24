import re, csv, sys, subprocess, os, glob, shutil
from utils.fileUtils import read_txt
from utils.decompose_log import decompose_detections

REG_PTR_TORCH = re.compile('torch.')
REG_PTR_TF = re.compile('tf.')

def make_str_clean(str_data):
    str_data = str_data.replace("{", "")
    str_data = str_data.replace("'", "")
    str_data = str_data.replace(",", "")
    str_data = str_data.replace(":", "")
    str_data = str_data.replace("}", "")
    return str_data

def save_nabla_log_torch(lib, tool, _version):
    if lib == "torch":
        _path_to_logs_old = f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/torch/{_version}/union/"

    if lib == 'torch':
        target_data = read_txt('/home/nimashiri/torch_test_apis_1.txt')
    
    output_path = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{_version}/label_frequency.csv"

    out_file = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{_version}/label_frequency.csv"
    if os.path.exists(out_file):
        os.remove(out_file)
        
    data_log_path = os.path.join(_path_to_logs_old,'log.txt')
    data = read_txt(data_log_path)

    dictt = {'FWD_VALUE': 0,'REV_VALUE': 0,'CRASH': 0,'NAN': 0,'FWD_STATUS': 0,'REV_STATUS':0, 'ND_GRAD': 0,'REV_FWD_GRAD': 0,'SKIP':0,'PASS': 0,'STATUS': 0,'SUCCESS': 0, 'GRAD_VALUE_MISMATCH': 0, 'VALUE_MISMATCH': 0, 'DIRECT_CRASH': 0, 'REV_CRASH': 0, 'FWD_CRASH': 0, 'REV_STATUS_MISMATCH': 0, 'REV_GRAD_FAIL': 0, 'FWD_GRAD_FAIL': 0, 'ND_FAIL': 0, 'ARGS_FAIL': 0, 'DIRECT_FAIL': 0, 'GRAD_NOT_COMPUTED': 0, 'RANDOM': 0, 'DIRECT_NAN': 0}    
    decomposed_log = decompose_detections(data, lib)
    for log in decomposed_log:
        if log[0] in target_data:
            for item in log:
                if "{" in item:
                    str_dat_i = make_str_clean(item)
                    x = str_dat_i.split(' ')
                    if x[0]:
                        for j in range(0, len(x),2):
                            dictt[x[j]] += int(x[j+1])

    for idx, item in dictt.items():
        with open(output_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([idx, item])
            
def save_nabla_log_tf(lib, tool, _version):
    if lib == "torch":
        _path_to_logs_old = f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/torch/{_version}/union"
    else:
        _path_to_logs_old = f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/NablaFuzz/NablaFuzz-TensorFlow/src/expr_outputs/{_version}/test"

    if lib == 'torch':
        target_data = read_txt('/home/nimashiri/torch_test_apis_1.txt')
    else:
        target_data = read_txt('/home/nimashiri/tf_test_apis_1.txt')
    
    output_path = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{_version}/label_frequency.csv"

    out_file = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{_version}/label_frequency.csv"
    if os.path.exists(out_file):
        os.remove(out_file)
        
    data_log_path = os.path.join(_path_to_logs_old, 'logs', '1', 'test-log.txt')
    data = read_txt(data_log_path)

    x = {'FWD_VALUE': 0,'REV_VALUE': 0,'CRASH': 0,'NAN': 0,'FWD_STATUS': 0,'REV_STATUS':0, 'ND_GRAD': 0,'REV_FWD_GRAD': 0,'SKIP':0,'PASS': 0,'STATUS': 0,'SUCCESS': 0, 'GRAD_VALUE_MISMATCH': 0, 'VALUE_MISMATCH': 0, 'DIRECT_CRASH': 0, 'REV_CRASH': 0, 'FWD_CRASH': 0, 'REV_STATUS_MISMATCH': 0, 'REV_GRAD_FAIL': 0, 'FWD_GRAD_FAIL': 0, 'ND_FAIL': 0, 'ARGS_FAIL': 0, 'DIRECT_FAIL': 0, 'GRAD_NOT_COMPUTED': 0, 'RANDOM': 0, 'DIRECT_NAN': 0}    

    for log in data:
        split_log = log.split(' ')
        v = 0
        for i in range(1, len(split_log),2):
            str_dat_i = make_str_clean(split_log[i])
            str_dat_ii = make_str_clean(split_log[i+1])
            x[str_dat_i] += int(str_dat_ii)

    for idx, item in x.items():
        with open(output_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([idx, item])

def capture_output(lib, iteration,_version, env_name, tool) -> None:
    if lib == "torch":
        _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/{iteration}/{_version}/torch/union/"
    else:
        _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-TensorFlow/output-ad/{iteration}/{_version}/torch/union/"
        
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
        tool_full_name = 'NablaFuzz-PyTorch-Jax'
    else:
        target_data = read_txt('data/tf_apis.txt')
        tool_full_name = 'NablaFuzz-TensorFlow'
        
    directory_path = os.listdir(_path_to_logs_old)
    directories = [item for item in directory_path if os.path.isdir(os.path.join(_path_to_logs_old, item))]
    for dir_ in directories:
        if 'torch.' in dir_ or 'tf.' in dir_:
            if dir_ in target_data:
                all_test_files = os.path.join(_path_to_logs_old, dir_, 'all')
                for test_file in os.listdir(all_test_files):
                    t = os.path.join(_path_to_logs_old, dir_, 'all', test_file)
                    shell_command = ["post_processing/capture_log_nablafuzz.sh",lib, _version, tool, env_name, str(iteration), t, tool_full_name]
                    subprocess.call(shell_command,shell=False)

def main():
    lib = sys.argv[1]
    iteration = sys.argv[2]
    release = sys.argv[3]
    env_name = sys.argv[4]
    capture_output(lib, iteration, release, env_name, 'NablaFuzz')


if __name__ == '__main__':
    main()