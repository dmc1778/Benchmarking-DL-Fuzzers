import os, csv, sys
import pandas as pd
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
from utils.fileUtils import read_txt, postprocess_test_statistics, write_to_csvV2

executed = False

class SummarizeTestCases:
    def __init__(self, tool_name, lib_name, iteration, release) -> None:
        self.tool_name = tool_name
        self.lib_name = lib_name
        if tool_name == 'ACETest':
            self.iteration = iteration - 1
        else:
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

        self.execution_flag = True
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
        
        self.docter_test_counter = {
            'crash': 0,
            'exception': 0,
            'fail': 0,
            'timeout': 0,
        }

        self.ace_test_counter = {
            'invalid': 0,
            'crash': 0,
            'timeout': 0,
            'OOM': 0,
        }

        self.titanfuzz_test_counter = {
            'crash': 0,
            'exception': 0,
            'hangs': 0,
            'flaky': 0,
            'notarget': 0,
            'valid': 0
        }
        
    def count_freefuzz_test_cases(self):
        global executed
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
        
        if not executed:
            headers = list(self.freefuzz_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests" , self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.freefuzz_test_counter = {key: 0 for key in self.freefuzz_test_counter}
        
    def count_deeprel_test_cases(self):
        global executed
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
                apis_extracted = pair.split('+')
                api_name =apis_extracted[0]
                if api_name not in target_data:
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
        
        if not executed:
            headers = list(self.deeprel_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests", self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests", self.tool_name)
        self.deeprel_test_counter = {key: 0 for key in self.deeprel_test_counter}

    def count_nabla_test_cases(self):
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        directory_path = os.listdir(self.nablafuzz_root_path)
        directories = [item for item in directory_path if os.path.isdir(os.path.join(self.nablafuzz_root_path, item))]
        for dir_ in directories:
            if 'torch.' in dir_ or 'tf.' in dir_:
                if dir_ in target_data:
                    all_test_files = os.path.join(self.nablafuzz_root_path, dir_, 'all')
                    for test_file in os.listdir(all_test_files):
                        t = os.path.join(self.nablafuzz_root_path, dir_, 'all', test_file)
    
    def count_docter_test_cases(self):
        def count_docTer_crash(crash_records):
            count = 0
            for j in range(1, len(crash_records)):
                split_records = crash_records[j].split(',')
                count += int(split_records[2])
            return count
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')
            
        directory_path = os.listdir(self.docter_root_path)
        crash_records = read_txt(os.path.join(self.docter_root_path, 'bug_list'))
        
        directories = [item for item in directory_path if os.path.isdir(os.path.join(self.docter_root_path, item))]
        for dir_ in directories:
            if dir_ in target_data:
                current_dir = os.path.join(self.docter_root_path, dir_)
                if os.path.isdir(current_dir):
                    if os.path.isfile(os.path.join(current_dir, 'failure_record')):
                        fail_records = read_txt(os.path.join(current_dir, 'failure_record'))
                        self.docter_test_counter['fail'] += len(fail_records)
                    if os.path.isfile(os.path.join(current_dir, 'exception_record')):
                        exception_records = read_txt(os.path.join(current_dir, 'exception_record'))
                        self.docter_test_counter['exception'] += len(exception_records)
                    if os.path.isfile(os.path.join(current_dir, 'timeout_record')):
                        timeout_record = read_txt(os.path.join(current_dir, 'timeout_record'))
                        self.docter_test_counter['timeout'] += len(timeout_record)
                
        self.docter_test_counter['crash'] += count_docTer_crash(crash_records)
 
        output_data = [self.lib_name, self.iteration, self.release] + list(self.docter_test_counter.values())
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.docter_test_counter = {key: 0 for key in self.docter_test_counter}
        
    def count_ace_test_cases(self):
        if self.lib_name== 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')


        results = pd.read_csv(os.path.join(self.acetest_root_path, 'res.csv'), encoding='utf-8', sep=',')
        filtered_results = results[results['api'].isin(target_data)]
        
        self.ace_test_counter['invalid'] = filtered_results.iloc[:, 5].sum()
        self.ace_test_counter['crash'] = filtered_results.iloc[:, 6].sum()
        self.ace_test_counter['timeout'] = filtered_results.iloc[:, 7].sum()
        self.ace_test_counter['OOM'] = filtered_results.iloc[:, 8].sum()

        output_data = [self.lib_name, self.iteration, self.release] + list(self.ace_test_counter.values())
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.ace_test_counter = {key: 0 for key in self.ace_test_counter}
    
    def count_titanfuzz_test_cases(self):
        if self.lib_name== 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        target_dirs = ['crash', 'exception', 'hangs', 'flaky', 'notarget', 'valid']
        counter = 0
        try:
            for dir_ in target_dirs:
                current_target_dir = os.path.join(self.titanfuzz_root_path, dir_)
                py_files = os.listdir(current_target_dir)
                if py_files:
                    for j, file_ in enumerate(py_files):
                        api_name = file_.split('_')[0]
                        if api_name in target_data:
                            self.titanfuzz_test_counter[dir_] += 1
                else:
                    self.titanfuzz_test_counter[dir_] += len(py_files)
                        
            output_data = [self.lib_name, self.iteration, self.release] + list(self.titanfuzz_test_counter.values())
            write_to_csvV2(output_data, "numtests" , self.tool_name)
            self.titanfuzz_test_counter = {key: 0 for key in self.titanfuzz_test_counter}
        
        except Exception as e:
            print(e)
    
    def count_atlasfuzz_test_cases(self):
        pass


if __name__ == '__main__':
    
    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    tool_name = 'DeepRel'
    tool_name_low = 'deeprel'
    
    if not os.path.isfile(f"statistics/numtests/{tool_name}_1.csv"):
        for k, v in lib.items():
            for iteration in range(1, 6):
                for release in v:
                    print(f'Library: {k}, Iteration: {iteration}, Release: {release}')
                    obj_= SummarizeTestCases(tool_name, k, iteration, release)
                    function_call = f'obj_.count_{tool_name_low}_test_cases()'
                    eval(function_call)
                    # obj_.count_freefuzz_test_cases()

    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    
    value_holder = []
    for k, v in lib.items():
        for release in v:
            data = pd.read_csv(f"statistics/numtests/{tool_name}_1.csv")
            value_holder.append(postprocess_test_statistics(data, tool_name, k, release))
    headers = list(data.columns.values)
    df = pd.DataFrame(value_holder, columns=headers)
    df.to_csv(f"statistics/numtests/{tool_name}_2.csv", )