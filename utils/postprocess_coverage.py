import os
import pandas as pd
from functools import reduce
import numpy as np
import csv

COVERAGE_FILES_PATH = "statistics/tosem/coverage"
TOTAL_COVERAGE = "total_coverage.csv"

def append_to_csv(file_path, data):
    with open(file_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)
                
def summarizeCoverage():
    
    fuzzers = os.listdir(COVERAGE_FILES_PATH)
    
    lib_info = {
        "torch":
            ["2.0.0", "2.0.1", "2.1.0"],
        "tf":
            ["2.11.0", "2.12.0", "2.13.0", "2.14.0"]
    }
    for fuzzer in fuzzers:
        # if fuzzer == 'DeepRel':
        #     continue
        holder = []
        for k, v in lib_info.items():
            for release in v:
                current_fuzzer_dir = os.path.join(COVERAGE_FILES_PATH, fuzzer)
                file_name = f"{current_fuzzer_dir}/{fuzzer}_{k}_{release}_coverage.csv"
                
                if not os.path.isfile(file_name):
                    continue
                
                coverage_data = pd.read_csv(file_name, encoding="utf-8", sep=",")
                
                average_coverage_branch = np.round(np.average(coverage_data.iloc[:, 4])*100, 2)
                average_coverage_stmt = np.round(np.average(coverage_data.iloc[:, 5])*100, 2)
                holder = holder + [average_coverage_branch, average_coverage_stmt]
                
        data = [fuzzer] + holder
        append_to_csv(TOTAL_COVERAGE, data)

def getAPINames(libname):
    api_name_holder = {
        'FreeFuzz': [],
        'DeepRel': [],
        'DocTer': [],
        'NablaFuzz': [],
        'ACETest': [],
        'titanfuzz': [],
        'atlasfuzz': []
    }
    fuzzers = os.listdir(COVERAGE_FILES_PATH)
    
    for fuzzer in fuzzers:
        current_fuzzer_dir = os.path.join(COVERAGE_FILES_PATH, fuzzer)
        file_name = f"{current_fuzzer_dir}/{fuzzer}_coverage.csv"
        coverage_data = pd.read_csv(file_name, encoding='utf-8', sep=',')
        
        filtered_df = coverage_data[coverage_data["lib_name"] == libname]

        for idx, row in filtered_df.iterrows():
            row_split = row['filePath'].split('/')

            api_name = [item for item in row_split if f"{libname}." in item]
            
            if fuzzer == 'titanfuzz':
                api_name = api_name[0].split('_')[0]
            elif fuzzer == 'DeepRel':
                apis_extracted = api_name[0].split('+')
                api_name =apis_extracted[0]
            elif fuzzer == 'DocTer':
                api_name = '.'.join(api_name[0].split('.')[0:-1])
            else:
                api_name = api_name[0]
            api_name_holder[fuzzer].append(api_name)
    

    sets = [set(lst) for lst in api_name_holder.values()]

    common_elements = set.intersection(*sets) if sets else set()

    print('')

if __name__ == '__main__':
    summarizeCoverage()
    #getAPINames('torch')