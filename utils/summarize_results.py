import os, csv

def read_txt(_path):
    with open(_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def write_to_csv(data, toolname):
    with open(f"statistics/{toolname}.csv", 'a', encoding="utf-8", newline='\n') as file_writer:
        write = csv.writer(file_writer)
        write.writerow(data)

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
    
    def count_freefuzz_test_cases(self):
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        test_counter = {
            'fail': 0,
            'potential-bug': 0,
            'success': 0,
            'crash': 0,
            'timeout': 0
        }
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
                        test_counter[oracle] += py_file_count
                        
        crashed_tests = read_txt(os.path.join(self.freefuzz_root_path,'runcrash.txt'))
        timedout_tests = read_txt(os.path.join(self.freefuzz_root_path,'timeout.txt'))
        
        test_counter['crash'] = len(crashed_tests)
        test_counter['timeout'] = len(timedout_tests)
        
        output_data = [self.lib_name, self.iteration, self.release] + list(test_counter.values())
        write_to_csv(output_data, self.tool_name)
                        
                        
if __name__ == '__main__':
    
    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    iterations = [1,2,3,4,5]
    for k, v in lib.items():
        for iteration in iterations:
            for release in v:
                print(f'Library: {k}, Iteration: {iteration}, Release: {release}')
                obj_= SummarizeTestCases('FreeFuzz', k, iteration, release)
                obj_.count_freefuzz_test_cases()