import os, sys, csv
import pandas as pd
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
from utils.fileUtils import read_txt

def capture_logs(lib, iteration,_version, tool):
    if lib == 'torch':
        full_lib_name = 'pytorch'
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
        docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{iteration}/{_version}+cu118/conform_constr"
    else:
        full_lib_name = 'tensorflow'
        ground_truth = pd.read_csv(f'data/{lib}_groundtruth.csv')
        docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{iteration}/{_version}/conform_constr"
    
    output_path  = f"/media/nimashiri/DATA/testing_results/tosem"
    file_path = os.path.join(docter_root_path, 'bug_list')
    if os.path.isfile(file_path):
        bug_list = read_txt(file_path)
        if len(bug_list)>1:
            for idx, row in ground_truth.iterrows():
                for j, item in enumerate(bug_list):
                    if j == 0:
                        continue
                    current_bug = item.split(',')
                    if row['Buggy API'] == current_bug[0]:
                        flag = row['Impact'] in current_bug
                        if flag and row['Version'] == _version:
                            output = [tool, lib, iteration, row['Issue'], row['Version'], _version, current_bug[0], row['Log Message'], current_bug[1]]
                            with open(f"{output_path}/detected_bugs.csv", "a", encoding="utf-8", newline='\n') as file:
                                write = csv.writer(file)
                                write.writerow(output)
                
if __name__ == '__main__':
    for lib in ['torch', 'tf']:
        for i in range(1, 6):
            if lib == 'tf':
                releases = ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
            else:
                releases = ['2.0.0', '2.0.1', '2.1.0']
            for release in releases:
                capture_logs(lib, i, release, 'DocTer')