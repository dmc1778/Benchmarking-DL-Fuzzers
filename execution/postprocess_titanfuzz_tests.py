import re, csv, sys, subprocess, os, glob, shutil

# REG_PTR = re.compile('Processing file')
# REG_PTR_ORION = re.compile('Running')

REG_PTR = re.compile('"""')
REG_PTR_ORION = re.compile('"""')
    
def remove_assertions(source_version, lib, tool):
    _path_to_logs_old = f"/media/nimashiri/SSD/testing_results/RQ1_determinism/titanfuzz/{tool}/{lib}/"
    if not os.path.exists(os.path.join(_path_to_logs_old, 'noAssertions')):
        os.makedirs(os.path.join(_path_to_logs_old, 'noAssertions'))

    target_dirs = ['exception']
    for dir_ in target_dirs:
        current_target_dir = os.path.join(_path_to_logs_old, dir_)
        py_files = os.listdir(current_target_dir)
        for file_ in py_files:
            code_path = os.path.join(current_target_dir, file_)
            code_ = read_txt(code_path)
            decomposed_ = decompose_detections(code_)
            decomposed_ = list(filter(lambda item: item != [], decomposed_))
            decom_ = ''.join(decomposed_[0])
            
            pattern = re.compile(r"(repeats must have|grad can be implicitly|Trying to|Could not infer|must be|isn't implemented|not implemented|Can only calculate|UserWarning|can't|The expanded size of the tensor|shapes cannot|but got|should be smaller than|does not require|must be in the range|The size of tensor|size mismatch|invalid|ambiguous|Expected|expected|A non-persistent GradientTape|NotFoundError|does not match shape of|Could not find device for node|Matrix is not positive definite|FailedPreconditionError|JSONDecodeError|Prepare() failed|KeyError|not supported|SyntaxError|AxisError|URL fetch failure on|is not allowed in Graph execution|is not compatible with|Attempting to capture an EagerTensor|referenced before assignment|The Session graph is empty.|UnimplementedError|No such file or directory|should be a function|can only be called|You must compile|is not supported|NotImplementedError|IndexError|ImportError|OSError|NameError|TypeError|AttributeError|unexpected keyword|InvalidArgumentError|ValueError)")

            if pattern.search(decom_):
                print(f'I am filtering {file_}')
                continue
            else:
                filtered_code = list(filter(lambda item: not re.findall(r'(assert)', item), code_))
                with open(os.path.join(_path_to_logs_old, f'noAssertions/{file_}'), "w") as file:
                    for line in filtered_code:
                        file.write(line + "\n")
                
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

def capture_output(_version, lib, tool, env_name) -> None:
    shell_command = ["/media/nimashiri/SSD/testing_results/capture_stderr.sh",lib, _version, tool, env_name]
    subprocess.call(shell_command,shell=False)

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines


def find_api_in_target(log_data_latest, target_api):
    log_decomposed = decompose_detections(log_data_latest)
    target_api_ = target_api.replace('.','\.')
    target_api_ = target_api_.replace('+','\+')
    
    # pattern_api = r'\b' + target_api + r'\b'
    out_api = []
    for log in log_decomposed:
        if "Processing file" in log[0] and re.findall(target_api_, log[0]):
            test_err_full = log[-5:]
            test_err_symp = log[-1]
            out_api.append(test_err_symp)
            out_api.append(test_err_full)
            break
    return out_api

def insert_dependency(_version, lib, tool):
    
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/titanfuzz/{lib}/{_version}/{lib}_{_version}/{lib}"
    target_dirs = ['crash','exception','flaky','hangs']
    for dir_ in target_dirs:
            current_target_dir = os.path.join(_path_to_logs_old, dir_)
            py_files = os.listdir(current_target_dir)
            for file_ in py_files:
                print(file_)
                code_path = os.path.join(current_target_dir, file_)
                code_ = read_txt(code_path)
                if lib == 'tf':
                    code_.insert(0, 'import tensorflow as tf')
                    code_.insert(1, 'import numpy as np')
                    code_.insert(2, 'import os')
                    code_.insert(2, 'import sys')
                else:
                    code_.insert(0, 'import torch')
                    code_.insert(1, 'import numpy as np')
                    code_.insert(2, 'import os')
                    code_.insert(2, 'import sys')
                with open(code_path, "w", encoding="utf-8", newline='\n') as out_file:
                    for line in code_:
                        out_file.write(line + "\n")
                        
def save_titanFuzz_results(lib, tool, release, new_release, env_, new_env, latest=False):
    out_dir = "/media/nimashiri/SSD/testing_results/"
    _path_to_logs_old = f"/media/nimashiri/SSD/testing_results/RQ1_determinism/titanfuzz/{tool}/{lib}/exception/{release}.txt"
    if latest:
        _path_to_logs_latest = f"/media/nimashiri/SSD/testing_results/{tool}/{lib}/{release}/exception/{new_release}.txt"
        log_data_latest = read_txt(_path_to_logs_latest)
    log_data_old = read_txt(_path_to_logs_old)
    
    log_decomposed = decompose_detections(log_data_old)
    for log in log_decomposed:
        if "Processing file" in log[0]:
            test_err_full = log[-5:]
            test_err_symp = log[-1]
            api_name = log[0].split('/')[9]
            api_name = api_name.replace('.py', '')
            if latest:
                latest_status = find_api_in_target(log_data_latest, api_name)
            print(api_name)

            if latest:
                output = [tool, release, api_name, test_err_symp, log, latest_status[0], latest_status[1]]
            else:
                output = [tool, release, api_name, test_err_symp, test_err_full]
            with open(f"{out_dir}{lib}_{tool}_{release}_HIGH_LEVEL.csv", "a", encoding="utf-8", newline='\n') as file:
                write = csv.writer(file)
                write.writerow(output)

def process(lib, iteration,_version, env_name, tool):
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')
    
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/Results/{lib}/{_version}/{iteration}"
    
    target_dirs = ['crash', 'exception', 'hangs', 'flaky']
    counter = 0
    try:
        for dir_ in target_dirs:
            current_target_dir = os.path.join(_path_to_logs_old, dir_)
            py_files = os.listdir(current_target_dir)
            for j, file_ in enumerate(py_files):
                api_name = file_.split('_')[0]
                print(file_)
                if api_name in target_data:
                    counter = counter + 1
                    print(f'{j}/{len(py_files)}')
                    counter = 0
                    code_path = os.path.join(current_target_dir, file_)
                    code_ = read_txt(code_path)
                    pure_api = re.sub(r'_\d+', '', file_)
                    
                    decomposed_ = decompose_detections(code_)
                    decomposed_ = list(filter(lambda item: item != [], decomposed_))
                        
                    decom_ = ''.join(decomposed_[0])

                    with open(f"{_path_to_logs_old}/{_version}.csv", "a", encoding="utf-8", newline='\n') as out_file:
                        write = csv.writer(out_file)
                        write.writerow([tool, _version, f"{dir_}/{file_}", decomposed_[0]])
    except Exception as e:
        print(e)


def main():
    lib = sys.argv[1]
    iteration = sys.argv[2]
    release = sys.argv[3]
    env_name = sys.argv[4]
    # process('tf', 1, "2.11.0", "tf_2.11.0", 'titanfuzz')
    process(lib, iteration, release, env_name, 'titanfuzz')


if __name__ == '__main__':
    main()