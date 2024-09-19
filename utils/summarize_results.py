import os, csv

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def write_to_csv(data, toolname):
    with open(f"statistics/{toolname}.csv", 'a', encoding="utf-8", newline='\n') as file_writer:
        write = csv.writer(file_writer)
        write.writerow(data)

def list_python_files(directory):
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

class SummarizeTestCases:
    def __init__(self, tool_name, lib_name, iteration, release) -> None:
        self.tool_name = tool_name
        self.lib_name = lib_name
        self.iteration = iteration
        self.release = release
        self.freefuzz_root_path  = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}"
        self.deeprel_root_path = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}/expr"
        
        if lib_name == 'torch':
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/{self.iteration}/{self.release}/torch/union/"
        else:
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-TensorFlow/output-ad/{self.iteration}/{self.release}/torch/union/"
        
        if lib_name == 'torch':
            full_lib_name = 'pytorch'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{self.iteration}/{self.release}+cu118/conform_constr"
        else:
            full_lib_name = 'tensorflow'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{self.iteration}/{self.release}/conform_constr"
        
        self.acetest_root_path = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/Tester/src/output/output_{self.lib_name}_{self.iteration}/{self.release}"
        
        self.titanfuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/titanfuzz/Results/{self.lib_name}/{self.release}/{self.iteration}"
        self.atlasfuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/code-{self.tool_name}/fewshot/output/{self.lib_name}_demo/{self.iteration}/{self.release}"

        self.freefuzz_test_counter = {
            'fail': 0,
            'potential-bug': 0,
            'success': 0,
            'crash': 0,
            'timeout': 0
        }

        self.deeprel_test_counter = {
            'bug': 0,
            'err': 0,
            'fail': 0,
            'neq': 0,
            'success': 0
        }
        
    def count_freefuzz_test_cases(self):
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')


        directory_path = os.listdir(self.freefuzz_root_path)
        directories = [item for item in directory_path if os.path.isdir(os.path.join(self.freefuzz_root_path, item))]
        for dir_ in directories:
            current_dir = os.path.join(self.freefuzz_root_path, dir_)
            for oracle in ['fail', 'potential-bug', 'success']:
                current_oracle = os.path.join(current_dir, oracle)
                current_apis = os.listdir(current_oracle)
                for api in current_apis:
                    if api in target_data:
                        test_files_path = os.path.join(current_oracle, api)
                        test_files_list = os.listdir(test_files_path)
                        py_file_count = len([file for file in test_files_list if file.endswith('.py')])
                        self.freefuzz_test_counter[oracle] += py_file_count
                        
        crashed_tests = read_txt(os.path.join(self.freefuzz_root_path,'runcrash.txt'))
        timedout_tests = read_txt(os.path.join(self.freefuzz_root_path,'timeout.txt'))
        
        self.freefuzz_test_counter['crash'] = len(crashed_tests)
        self.freefuzz_test_counter['timeout'] = len(timedout_tests)
        
        output_data = [self.lib_name, self.iteration, self.release] + list(self.freefuzz_test_counter.values())
        write_to_csv(output_data, self.tool_name)
        self.freefuzz_test_counter = {key: 0 for key in self.freefuzz_test_counter}
        
    def count_deeprel_test_cases(self):
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        directories = ['output-0']
        for dir_ in directories:
            current_dir = os.path.join(self.deeprel_root_path, dir_)
            all_dirs = os.listdir(current_dir)
            for pair in all_dirs:
                if "+" not in pair:
                    continue
                current_api_pair= os.path.join(current_dir, pair)
                current_oracles = os.listdir(current_api_pair)
                for oracle in ['bug', 'err', 'fail', 'neq', 'success']:
                    target_ = os.path.join(current_api_pair, oracle)
                    if not os.path.exists(target_):
                        continue
                    test_files_list = os.listdir(target_)
                    py_file_count = len([file for file in test_files_list if file.endswith('.py')])
                    self.deeprel_test_counter[oracle] += py_file_count
        output_data = [self.lib_name, self.iteration, self.release] + list(self.deeprel_test_counter.values())
        write_to_csv(output_data, self.tool_name)
        self.deeprel_test_counter = {key: 0 for key in self.deeprel_test_counter}
                        
if __name__ == '__main__':
    
    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    for k, v in lib.items():
        for iteration in range(1, 6):
            for release in v:
                print(f'Library: {k}, Iteration: {iteration}, Release: {release}')
                obj_= SummarizeTestCases('DeepRel', k, iteration, release)
                obj_.count_deeprel_test_cases()