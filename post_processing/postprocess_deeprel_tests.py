import re, csv, sys, subprocess, os, glob, shutil

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def find_apis(x, target_data):
    flag = False
    for api in x:
        flag = True
    return flag

def list_python_files(directory):
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

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
                    
if __name__ == '__main__':
    # lib = sys.argv[1]
    # iteration = sys.argv[2]
    # release = sys.argv[3]
    # env_name = sys.argv[4]
    
    lib = 'torch'
    iteration = 1
    release = '2.0.0'
    env_name = 'torch_2.0.0'

    capture_output(lib, iteration, release, env_name, 'DeepRel')