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

def save_freefuzz_results(lib, tool, release):
    
    if lib == 'torch':
        target_data = read_txt('/home/nimashiri/torch_test_apis_1.txt')
    else:
        target_data = read_txt('/home/nimashiri/tf_test_apis_1.txt')

    log_data_old = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{release}/{release}.txt"
    output_dir = f"/media/nimashiri/DATA/testing_results/{tool}/{lib}/{release}/"
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
    tools = ['FreeFuzz']
    for tool in tools:
        for lib in libs:
            if lib == "tf":
                releases = releases_tf
            else:
                releases = releases_torch
            for release in releases:
                count_additional_success(release, lib, tool)
                # save_freefuzz_results(lib, tool, release)
    

if __name__ == '__main__':
    main()