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
    _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/{tool}/{lib}/{iteration}/{_version}"
    if lib == 'torch':
        target_data = read_txt('data/tf_apis.txt')
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
            for api in current_apis:
                if api in target_data:
                    shell_command = ["post_processing/capture_log.sh",lib, _version, tool, env_name, dir_, oracle, api, str(iteration)]
                    subprocess.call(shell_command,shell=False)

def save_freefuzz_logs(lib, tool, release):
    if lib == 'torch':
        target_data = read_txt('/home/nimashiri/torch_apis.txt')
    else:
        target_data = read_txt('/home/nimashiri/tf_apis.txt')
    
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
    # tool = sys.argv[1]
    # lib = sys.argv[2]
    # source_version = sys.argv[3]

    # tool = "FreeFuzz"
    # lib = "tf"
    # source_version = "2.11.0"
    
    releases_tf = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
    releases_torch = ["2.0.0", "2.0.1", "2.1.0"]
    libs = ["tf","torch"]
    task = 'capture'
    
    for lib in libs:
        for iteration in range(1, 5):
            if lib == "tf":
                releases = releases_tf
            else:
                releases = releases_torch
            for release in releases:
                env_name = f"{lib}_{release}"
                if task == 'capture':
                    capture_output(lib, iteration, release, env_name, 'FreeFuzz')
                else:
                    save_freefuzz_logs(lib, 'FreeFuzz', release)
    
if __name__ == '__main__':
    main()