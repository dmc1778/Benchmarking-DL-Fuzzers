import os
import pandas as pd
from functools import reduce

COVERAGE_FILES_PATH = "statistics/tosem/coverage"

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
    getAPINames('torch')