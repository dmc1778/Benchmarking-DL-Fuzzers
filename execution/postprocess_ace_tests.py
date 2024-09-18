import re, csv, sys, subprocess, os, glob, shutil
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

def save_ace_logs(lib, tool, release):
    if lib == 'torch':
        target_data = read_txt('data/torch_apis.txt')
    else:
        target_data = read_txt('data/tf_apis.txt')
    
    log_data_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{release}/{release}.txt"
    output_dir = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{release}/"
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
    iteration = int(sys.argv[2])
    release = sys.argv[3]
    env_name = sys.argv[4]

    capture_output(lib, iteration, release, env_name, 'ACETest')
    # capture_output('tf', 1, '2.11.0', 'tf_2.11.0', 'ACETest')

if __name__ == '__main__':
    main()