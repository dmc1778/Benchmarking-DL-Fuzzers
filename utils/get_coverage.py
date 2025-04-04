import os
import sys
import subprocess
import signal
import json
import random, csv
# import tensorflow as tf
# import torch
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
from utils.fileUtils import read_txt, load_json
ROOT_PATH=os.getcwd()
import uuid, re, inspect, importlib
import numpy as np
import multiprocessing


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def write_csv_headers(file_path, headers):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def append_to_csv(file_path, data):
    with open(file_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)
        
def get_api_source(api_str):
    parts = api_str.split('.')
    if parts[0] == 'tf':
        parts[0] = 'tensorflow'
    module = importlib.import_module(parts[0])
    obj = module
    for part in parts[1:]:
        obj = getattr(obj, part)
    
    try:
        return inspect.getfile(obj)
    except TypeError:
        if inspect.isbuiltin(obj):
            mod = inspect.getmodule(obj)
            if mod is not None and hasattr(mod, '__file__'):
                return mod.__file__
            else:
                return f"Source file not available for built-in function {api_str}"
        else:
            return f"Source file not available for {api_str}"

class CalculateCoverage:
    def __init__(self, tool_name, lib_name, iteration, release, venue):
        self.tool_name = tool_name
        self.lib_name = lib_name
        self.venue = venue
        self.release = release
        self.iteration = iteration
        
        if lib_name == 'torch':
            self.libname_small = 'torch'
        else:
            self.libname_small = 'tf' 
        
        self.freefuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}"
        self.deeprel_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}/expr"

        if lib_name == 'torch':
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/{self.iteration}/{self.release}/torch/union/"
        else:
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/NablaFuzz/NablaFuzz-TensorFlow/src/expr_outputs/{self.iteration}/{self.release}/test/logs/"

        if lib_name == 'torch':
            full_lib_name = 'pytorch'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/workdir/{full_lib_name}/{self.iteration}/{self.release}+cu118/conform_constr"
        else:
            full_lib_name = 'tensorflow'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/workdir/{full_lib_name}/{self.iteration}/{self.release}/conform_constr"
        
        self.acetest_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/{self.tool_name}/Tester/src/output/output_{self.lib_name}_{self.iteration}/{self.release}"
        
        self.titanfuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/titanfuzz/Results/{self.lib_name}/{self.release}/{self.iteration}"
        self.atlasfuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/code-{self.tool_name}/fewshot/output/{self.lib_name}_demo/{self.iteration}/{self.release}"

        self.atlasfuzz_root_path = f"/media/nimashiri/DATA/testing_results/{self.venue}/code-{self.tool_name}/fewshot/output/{self.lib_name}_demo/{self.iteration}/{self.release}"

        self.env_name = f"{self.libname_small}_{release}"
        self.lib_src = f"/home/nimashiri/anaconda3/envs/{self.env_name}/lib/python3.9/site-packages/{self.lib_name}"

    def get_import_statement(self, module_file_path, site_packages_path):
        if self.lib_name == 'tf':
            libname_ = 'tensorflow'
        else:
            libname_ = self.lib_name
        module_path_split = module_file_path.split(libname_)

        sub_split = module_path_split[-1].split('/')
        sub_split = [item for item in sub_split if item]
        import_part = sub_split[0:-1]
        after_ = sub_split[-1].replace('.py', '')
        
        import_part = ".".join(import_part)
        
        import_full = f"from {libname_}.{import_part} import {after_}"
        return import_full

    def run_coverage(self, target_file, output_w, csv_file, api_name, titanflag=False):
        api_source = get_api_source(api_name)
        # module_import_stmt = self.get_import_statement(api_source, self.lib_src)
        api_source = os.path.dirname(api_source)
        
        # with open(target_file, "r") as file:
        #     content = file.read()
        
        # content = f"{module_import_stmt}\n" + content
        
        # test_file_name = f"{self.tool_name}_{self.lib_name}_{self.release}.py"
        # with open(test_file_name, "w") as file:
        #     file.write(content)
        
        coverage_file_path = os.path.join(output_w, f".coverage_{self.tool_name}_{self.lib_name}_{self.release}")
        json_file_path = f"{output_w}/{self.tool_name}_{self.lib_name}_{self.release}.json"
        

        print(f"calculating coverage for {self.tool_name} ::: {self.lib_name} ::: {self.release} ::: {target_file}")
        
        if titanflag:
            if self.lib_name == 'torch':
                cov_cmd = f'coverage run --branch --data-file={coverage_file_path} --source={api_source} test_{self.lib_name}.py'
            else:
                cov_cmd = f'coverage run --branch --data-file={coverage_file_path} --source={api_source} test_{self.lib_name}.py'    
        else:
            if self.lib_name == 'torch':
                cov_cmd = f'coverage run --branch --data-file={coverage_file_path} --source={api_source} {target_file}'
            else:
                cov_cmd = f'coverage run --branch --data-file={coverage_file_path} --source={api_source} {target_file}'
            
        cov_cmd_json = f'coverage json --data-file={coverage_file_path} -o {json_file_path}'
        
        signal.alarm(60)
        try:
            subprocess.run(cov_cmd, shell=True)
            subprocess.run(cov_cmd_json, shell=True)
            cov_info_ = load_json(json_file_path)
                
            totals = cov_info_.get("totals", {})
            file_names = cov_info_.get('files', {})
            
            branch_coverage = totals['covered_branches'] / totals['num_branches']
            statement_coverage = totals['covered_lines'] / totals['num_statements']
            write_csv_headers(csv_file, ["tool_name", "lib_name", "release", "filePath", 'percent_covered'])            
            append_to_csv(csv_file, [self.tool_name, self.lib_name, self.release, target_file, branch_coverage, statement_coverage])
            
            subprocess.run(f"rm {coverage_file_path}", shell=True)
            subprocess.run(f"rm {json_file_path}", shell=True)
        except TimeoutException:
            pass 
        else:
            signal.alarm(0)

    def get_coverage_json(self):
        global executed
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        output_w = f'statistics/{self.venue}/coverage/{self.tool_name}'

        
        csv_file = f"{output_w}/{self.tool_name}_{self.lib_name}_{self.release}_coverage.csv"

        os.makedirs(output_w, exist_ok=True)
        signal.signal(signal.SIGALRM, timeout_handler)
        
        if self.tool_name == 'FreeFuzz':
            directory_path = os.listdir(self.freefuzz_root_path)
            directories = [item for item in directory_path if os.path.isdir(os.path.join(self.freefuzz_root_path, item))]
            for dir_ in directories:
                current_dir = os.path.join(self.freefuzz_root_path, dir_)
                for oracle in ['potential-bug']:
                    current_oracle = os.path.join(current_dir, oracle)
                    current_apis = os.listdir(current_oracle)
                    for api in current_apis:
                        if api in target_data:
                            test_files_path = os.path.join(current_oracle, api)
                            test_files_list = os.listdir(test_files_path)
                            if len(test_files_list) > 1:
                                test_files_list = random.sample(test_files_list, 1)
                            for file in test_files_list:
                                target_file = os.path.join(test_files_path, file)
                                try:
                                    self.run_coverage(target_file, output_w, csv_file, api, False)
                                except Exception as e:
                                    print(e)
                                
        elif self.tool_name == 'DeepRel':
            directories = ['output-0']
            for dir_ in directories:
                current_dir = os.path.join(self.deeprel_root_path, dir_)
                all_dirs = os.listdir(current_dir)
                for pair in all_dirs:
                    
                    if "+" not in pair:
                        continue
                    
                    if 'rel+0' in pair or 'rel+1' in pair:
                        continue
                    apis_extracted = pair.split('+')
                    api_name =apis_extracted[0]
                    if api_name not in target_data:
                        continue
                    current_api_pair= os.path.join(current_dir, pair)
                    for oracle in ['err', 'fail', 'neq']:
                        target_ = os.path.join(current_api_pair, oracle)
                        if not os.path.exists(target_):
                            continue
                        test_files_list = os.listdir(target_)
                        
                        if len(test_files_list) > 1:
                            test_files_list = random.sample(test_files_list, 1)
                        for file in test_files_list:
                            target_file = os.path.join(target_, file)
                            try:
                                self.run_coverage(target_file, output_w, csv_file, api_name, False)
                            except Exception as e:
                                print(e)
                            
        elif self.tool_name == 'NablaFuzz':
            if self.lib_name == 'torch':
                dirs = os.listdir(os.path.join(self.nablafuzz_root_path))
                for item in dirs:
                    if 'torch.' in item:
                        if item in target_data:
                            current_api_dir = os.path.join(self.nablafuzz_root_path, item, 'all')
                            current_test_files = os.listdir(current_api_dir)
                            if len(current_test_files) > 1:
                                test_files_list = random.sample(current_test_files, 1)
                            for file in test_files_list:
                                target_file = os.path.join(current_api_dir, file)
                                try:
                                    self.run_coverage(target_file, output_w, csv_file, item, False)
                                except Exception as e:
                                    print(e)
        
        elif self.tool_name == 'DocTer':
            for dir_ in os.listdir(self.docter_root_path):
                dir__ = ".".join(dir_.split('.')[0:-1])
                if dir__ in target_data:
                    api_name = os.path.join(self.docter_root_path,dir_)
                    files = os.listdir(api_name)
                    files = [file for file in files if file.endswith('.py')]
                    if len(files) > 1:
                        files = random.sample(files, 1)
                    for file in files:
                        test_file_path = os.path.join(api_name,file)
                        with open(test_file_path, "r") as file:
                            content = file.read()

                        if self.lib_name == 'torch':
                            updated_content = re.sub(
                                r"(/home/nima/)(workdir/pytorch/)",
                                r"/media/nimashiri/DATA/testing_results/tosem/\g<2>1/",
                                content
                            )
                        else:
                            updated_content = re.sub(
                                r"(/home/nima/)(workdir/tensorflow/)",
                                r"/media/nimashiri/DATA/testing_results/tosem/\g<2>1/",
                                content
                            )
                        with open(test_file_path, "w") as file:
                            file.write(updated_content)
                        
                        try:
                            self.run_coverage(test_file_path, output_w, csv_file, dir__)
                        except Exception as e:
                            print(e)
                                
        elif self.tool_name == 'ACETest':
            api_dirs = os.listdir(self.acetest_root_path)
            for api in api_dirs:
                if api in target_data:
                    # oracles = os.listdir(os.path.join(self.acetest_root_path, api))
                    for oracle in ['crash', 'invalid']:
                        test_files_list = os.listdir(os.path.join(self.acetest_root_path, api, oracle))
                        if len(test_files_list) > 1:
                            test_files_list = random.sample(test_files_list, 1)
                        for file in test_files_list:
                            if file.endswith('.py'):
                                test_file_path = os.path.join(self.acetest_root_path,api,oracle,file)
                                try:
                                    self.run_coverage(test_file_path, output_w, csv_file, api, False)
                                except Exception as e:
                                    print(e)
                                    
        elif self.tool_name == 'titanfuzz':
            memory = []
            target_dirs = ['crash', 'exception', 'hangs', 'flaky', 'valid']
            try:
                for dir_ in target_dirs:
                    current_target_dir = os.path.join(self.titanfuzz_root_path, dir_)
                    py_files = os.listdir(current_target_dir)
                    if py_files:
                        for j, file_ in enumerate(py_files):
                            api_name = file_.split('_')[0]
                            if api_name in target_data and api_name not in memory:
                                test_file_path = os.path.join(current_target_dir, file_)
                            
                                with open(test_file_path, "r") as file:
                                    content = file.read()
                                    
                                if self.lib_name == 'torch':
                                    updated_content = "import torch\n" + content
                                    updated_content = "import numpy as np\n" + updated_content
                                else:
                                    updated_content = "import tensorflow as tf\n" + content
                                    updated_content = "import numpy as np\n" + updated_content

                                with open(f"test_{self.lib_name}.py", "w") as file:
                                    file.write(updated_content)
                                try:
                                    self.run_coverage(test_file_path, output_w, csv_file, api_name, True)
                                except Exception as e:
                                    print(e)
                                    
                                memory.append(api_name)
                                subprocess.run(f"rm test_{self.lib_name}.py", shell=True)

            except Exception as e:
                print(e)
        
        elif self.tool_name == 'atlasfuzz':
            current_dirs = os.listdir(self.atlasfuzz_root_path)
            for api in current_dirs:
                if api in target_data:
                    current_api = os.path.join(self.atlasfuzz_root_path, api)
                    test_files_list = os.listdir(current_api)
                    if len(test_files_list) > 1:
                        test_files_list = random.sample(test_files_list, 1)
                    for file in test_files_list:
                        if file.endswith('.py'):
                            test_file_path = os.path.join(self.atlasfuzz_root_path,api,file)
                            try:
                                self.run_coverage(test_file_path, output_w, csv_file, api, False)
                            except Exception as e:
                                print(e)
        else:
            return 

        # with multiprocessing.Pool(10) as pool:
        #     try:
        #         for _ in pool.imap_unordered(self.run_coverage, tasks):
        #             pass
        #     finally:
        #         pool.close()
        #         pool.join()
        #         pool.terminate()
    
def api_name_to_module(api_name):
    parts = api_name.split('.')
    if len(parts) == 1:
        return importlib.import_module(api_name)
    module_name = '.'.join(parts[:-1])
    attr_name = parts[-1]
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)
                           
if __name__=="__main__": 
    tool_name = sys.argv[1]
    libname =  sys.argv[2]
    iteration = sys.argv[3]
    release = sys.argv[4]
    venue = sys.argv[5]
    
    # tool_name = 'DocTer'
    # libname = 'torch'
    # iteration = 1
    # release = "2.0.0"
    # venue = 'tosem'
    
    obj_= CalculateCoverage(tool_name, libname, iteration, release, venue)
    obj_.get_coverage_json()