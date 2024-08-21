
import pandas as pd
import sys
sys.path.append('/home/nima/repository/Benchmarking-DL-Fuzzers')
from utils.io import load_csv, write_to_csv

HEADER = ['Library','Issue Link','Date','Title','API Name','Library Version','CUDA Version']

def count_apis(cell_string):
    api_list = cell_string.split()
    return api_list

def flat_multiple_apis(data, fname):
    for idx, row in data.iterrows():
        apis_separated = count_apis(row['API Name'])
        for api in apis_separated:
            output_list = [row['Library'], row['Issue Link'],row['Date'],row['Title'],api ,row['Library Version'],row['CUDA Version']]
            write_to_csv('data',fname,output_list)
            
if __name__ == '__main__':
    libnmae = 'tensorflow'
    fname = f"{libnmae}ManualStage2"
    data = load_csv(fname)
    flat_multiple_apis(data, fname)