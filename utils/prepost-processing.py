import pymongo
import os, csv
import re, shutil
import subprocess
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from csv import writer
import pandas as pd

logging.basicConfig(level=logging.INFO)

"""
MongoDB configurations
"""

# DB = pymongo.MongoClient(host="localhost", port=27017)["TF-Unique"]
client = MongoClient(
    "mongodb://localhost:27017/", serverSelectionTimeoutMS=10, connectTimeoutMS=300
)
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

rootCause = {
    "Category": {
      "API Input Context": {
        "Modeling Parameter Space": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Inputs with Incompatible Shapes": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Specific Data Types": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Large Integer Argument": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Large List Element": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Empty List Element": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Large Input Tensor": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Zero Input Tensor": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Negative Input Tensor": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Negative Integer Argument": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Specific Data Types": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Zero Integer Argument": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Empty Input Tensor": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Others": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        }
      },
      "Test Case Context": {
        "Modeling Multiple API Usage Pattern+Modeling Compile/Eager Execution Mode": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Complex Tensor Operations and Layer Interactions": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Complex Tensor Operations and Layer Interactions+Modeling Compile/Eager Execution Mode": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Complex Tensor Operations and Layer Interactions+Modeling Multiple API Usage Pattern": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Oracle for Performance Bug Detection": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Multiple API Usage Pattern": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Supporting External Library API": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Model Tensor Execution on CUDA Devices": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Compile/Eager Execution Mode": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Complex Tensor Operations and Layer Interactions": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Model XLA Compilation": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Model XLA Compilation+Model Tensor Execution on CUDA Devices": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Others": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        }
      },
      "Test Case Context+API Input Context": {
        "Modeling Complex Tensor Operations and Layer Interactions+Modeling Parameter Space": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Modeling Multiple API Usage Pattern+Modeling Parameter Space": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
        "Model XLA Compilation+Modeling Parameter Space": {
          "FreeFuzz": {"torch": "-", "tf": "-"},
          "DeepRel": {"torch": "-", "tf": "-"},
          "DocTer": {"torch": "-", "tf": "-"},
          "ACETest": {"torch": "-", "tf": "-"},
          "TitanFuzz": {"torch": "-", "tf": "-"},
          "FuzzGPT": {"torch": "-", "tf": "-"}
        },
      }
    }
  }
  

"""
Constants
"""

def write_list_to_txt4(data, filename):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(data + "\n")


def read_txt(fname):
    with open(fname, "r") as fileReader:
        data = fileReader.read().splitlines()
    return data


def drop_collection_condition(dbname):
    c = 0
    mydb = myclient[dbname]
    for api_name in mydb.list_collection_names():
        if re.findall(r"(\_\_main_\_\.)", api_name):
            print(api_name)
            mydb.drop_collection(api_name)


def count_value_space(dbname):
    source_dict = {"docs": 0, "tests": 0, "models": 0}
    mydb = myclient[dbname]
    for api_name in mydb.list_collection_names():
        mycol = mydb[api_name]
        count_test = mycol.count_documents({"source": "tests"})
        count_models = mycol.count_documents({"source": "models"})
        count_docs = mycol.count_documents({"source": "docs"})
        source_dict["tests"] = source_dict["tests"] + count_test
        source_dict["models"] = source_dict["models"] + count_models
        source_dict["docs"] = source_dict["docs"] + count_docs
        print(source_dict)


"""
This function returns a new database in which all documents are distinct.
The distinction is based the first parameter of each the documents in each collection.
"""


def get_unique_documents(dbname, new_db_name):
    QUERIED_APIS_ADDRESS = f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/logs/{dbname}_queried_apis.txt"
    new_db = pymongo.MongoClient(host="localhost", port=27017)[new_db_name]
    mydb = myclient[dbname]

    if not os.path.exists(QUERIED_APIS_ADDRESS):
        f1 = open(QUERIED_APIS_ADDRESS, "a")

    hist = read_txt(QUERIED_APIS_ADDRESS)

    for api_name in mydb.list_collection_names():
        if api_name not in hist:
            logging.info("Geting unique records for API: {0}".format(api_name))
            mycol = mydb[api_name]
            x = mycol.aggregate(
                [
                    {"$group": {"_id": "$parameter:0", "doc": {"$first": "$$ROOT"}}},
                    {"$replaceRoot": {"newRoot": "$doc"}},
                ]
            )

            x = list(x)
            for item in x:
                new_db[api_name].insert_one(item)
            write_list_to_txt4(api_name, QUERIED_APIS_ADDRESS)
        else:
            logging.info("{0} already inserted!".format(api_name))


def drop_database(dbname):
    myclient.drop_database(dbname)



"""
Count the number of APIs based on the source they have been collected. 
"""


def count_sources_per_api(dbname):
    QUERIED_APIS_ADDRESS = f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/logs/{dbname}_queried_apis.txt"
    mydb = myclient[dbname]
    counter = 0

    if not os.path.exists(QUERIED_APIS_ADDRESS):
        f1 = open(QUERIED_APIS_ADDRESS, "a")

    hist = read_txt(QUERIED_APIS_ADDRESS)

    for name in mydb.list_collection_names():
        if name not in hist:
            print("{}:{}".format(name, counter))
            write_list_to_txt4(name, QUERIED_APIS_ADDRESS)
            counter = counter + 1
            mycol = mydb[name]

            source_dict = {}
            for source in ["docs", "tests", "models"]:
                source_dict[source] = mycol.count_documents({"source": source})

            for k, v in source_dict.items():
                if v != 0:
                    mydata = [name, k]
                    with open(
                        f"/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/logs/{dbname}_api_coverage.csv",
                        "a",
                        newline="\n",
                    ) as fd:
                        writer_object = writer(fd)
                        writer_object.writerow(mydata)


def count_all_apis(dbname):
    DB = pymongo.MongoClient(host="localhost", port=27017)[dbname]

    counter = 0
    for name in DB.list_collection_names():
        counter = counter + 1
    print(counter)


def get_all_databases():
    print(myclient.list_database_names())

def count_overlap_docter(libname):
    j = 0
    files = os.listdir(f"/home/nimashiri/code/docter/all_constr/{libname}")
    for api in files:
        api = ".".join(api.split('.')[0:-1])
        flag = search_in_dataset(api, libname)
        if flag:
            write_list_to_txt4(api, f"statistics/overlap/DocTer_{libname}.txt")

        
def get_overlap_docter(libname):
    files = os.listdir(f"/home/nimashiri/code/docter/all_constr/{libname}")
    for api in files:
        api = ".".join(api.split('.')[0:-1])
        dst_path = os.path.join(f"/home/nimashiri/code/docter/all_constr/{libname}", api)
        api_split = api.split(".")
        new_api = ".".join(api_split[0:-1])
        flag = search_in_dataset(new_api, libname)
        if flag:
            if not os.path.exists(f'/home/nimashiri/code/docter/all_constr/{libname}'):
                os.makedirs(f'/home/nimashiri/code/docter/all_constr/{libname}')
            shutil.copy(dst_path, f'/home/nimashiri/code/docter/all_constr/{libname}')
                
def remove_overlap_docter(libname):
    files = os.listdir(f"/home/nimashiri/Desktop/nima_constr/{libname}")
    i = 0
    for api in files:
        api_split = api.split(".")
        new_api = ".".join(api_split[0:-1])
        flag = search_in_dataset(new_api, libname)
        if not flag:
            os.remove(
                os.path.join(f"/home/nimashiri/Desktop/nima_constr/{libname}", api)
            )
            i = i + 1
            print(f"Found non overlapping api{new_api}:{i}")


def search_in_dataset(api_name, lib):
    flag = False
    if lib == "pt" or lib == 'torch' or lib == 'torch':
        data = read_txt(
            "data/torch_apis.txt"
        )
    else:
        data = read_txt(
            "data/tf_apis.txt"
        )
    for item in data:
        if api_name == item:
            flag = True
            break
    return flag


def get_overlap_freefuzz_deeprel_nablafuzz(dbname, lib, toolName):
    DB = pymongo.MongoClient(host="localhost", port=27017)[dbname]
    i = 0
    for api_name in DB.list_collection_names():
        flag = search_in_dataset(api_name, lib)
        if flag:
            write_list_to_txt4(api_name, f"statistics/overlap/{toolName}_{lib}.txt")

"""
Delete all documents in a collection based on the field source.
"""

def drop_document(apiName, dbname):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[dbname]
    result = db.drop_collection(apiName)
    if result:
        print("Collection dropped successfully.")
    else:
        print("Collection does not exist.")

def get_single_api(api, dbname):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[dbname]
    try:
        db.validate_collection(api)
        return True
    except pymongo.errors.OperationFailure:
        return False

def remove_object_files(api_name, libname):
    if libname == 'torch':
        libnameBig = 'torch'
        os.remove(f"~/NablaFuzz/NablaFuzz-{libnameBig}-Jax/dump/{libname}/{api_name}.metadata.json")
        os.remove(f"~/NablaFuzz/NablaFuzz-{libnameBig}-Jax/dump/{libname}/{api_name}.bson")
    if libname == 'tf':
        libnameBig = 'tf'
        os.remove(f"~/NablaFuzz/NablaFuzz-{libnameBig}/dump/{libname}/{api_name}.metadata.json")
        os.remove(f"~/NablaFuzz/NablaFuzz-{libnameBig}/dump/{libname}/{api_name}.bson")  
    
def remove_non_overlap_from_mongodb(libname):
    if libname == "torch":
        data = read_txt(
            "data/torch_apis.txt"
        )
    else:
        data = read_txt(
            "data/tf_apis.txt"
        )
    client = MongoClient('mongodb://localhost:27017/')
    db = client[libname]
    for api_name in db.list_collection_names():
        if api_name in data:
            print(f'API {api_name} exists, so I keep it!')
        else:
            if get_single_api(api_name, libname):
                drop_document(api_name, libname)
                # remove_object_files(api_name, libname)
        
def count_overlap_ace(libname):
    data = pd.read_csv(f"data/ace_{libname}.csv")
    for idx, row in data.iterrows():
        api_name = row.iloc[0].split(" ")[0]
        flag = search_in_dataset(api_name, libname)
        if flag:
            write_list_to_txt4(api_name, f"statistics/overlap/ACETest_{libname}.txt")

def count_overlap_titanfuzz(libname):
    target_apis = read_txt(f"data/titanfuzz_apis/{libname}_apis.txt")
    for api_name in target_apis:
        flag = search_in_dataset(api_name, libname)
        if flag:
            write_list_to_txt4(api_name, f"statistics/overlap/TitanFuzz_{libname}.txt")

def count_overlap_fuzzgpt(libname):
    target_apis = read_txt(f"data/fuzzgpt_apis/{libname}_apis.txt")
    for api_name in target_apis:
        flag = search_in_dataset(api_name, libname)
        if flag:
            write_list_to_txt4(api_name, f"statistics/overlap/FuzzGPT_{libname}.txt")
            
def summarizedMissedBugs(libname, toolname):
    overlap_apis = read_txt(f'statistics/overlap/{toolname}_{libname}.txt')
    data = pd.read_csv(f"data/{libname}_groundtruth.csv", sep=',', encoding='utf-8')
    filtered_results = data[data['Buggy API'].isin(overlap_apis)]
    toolname = [toolname]
    filtered_results = filtered_results[~(filtered_results['Detected1'].isin(toolname) | filtered_results['Detected2'].isin(toolname))]
    if toolname == 'ACETest':
        filtered_results = filtered_results[filtered_results['Detected'] != 'ace_1']
    print(f"{toolname}-{libname}:{filtered_results.shape}")
    if not os.path.isdir(f"statistics/missedBugs/{toolname}/"):
        os.mkdir(f"statistics/missedBugs/{toolname}/")
    #x = filtered_results['Trigger'].value_counts()
    x = filtered_results.groupby(['Category', 'Trigger']).size().reset_index(name='Frequency')
    
    # for idx, row in x.iterrows():
    #     rootCause['Category'][row['Category']][row['Trigger']][toolname][libname] = row['Frequency']
    
    x.to_csv(f'statistics/missedBugs/{toolname[0]}/{toolname[0]}_missed_bugs_{libname}.csv', index=True)

    # Helper function to flatten the nested dictionary
def flatten_dict(d, parent_key='', sep=' > '):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
def main():
    ## Step 1
    # for tool in ['FreeFuzz', 'DeepRel', 'NablaFuzz']:
    #     get_overlap_freefuzz_deeprel_nablafuzz('tf', 'tf', tool)
    # count_overlap_docter('pt')
    # count_overlap_ace('torch')
    # count_overlap_titanfuzz('torch')
    # count_overlap_fuzzgpt('torch')
    
    ## Step 2
    # ['FreeFuzz', 'DeepRel', 'DocTer', 'ACETest', 'FuzzGPT', 'TitanFuzz'] 
    for tool in ['FreeFuzz', 'DeepRel', 'DocTer', 'ACETest', 'TitanFuzz', 'FuzzGPT']:
        for lib in ['torch', 'tf']:
            summarizedMissedBugs(lib, tool)

    import json
    with open('rootcause.json', 'w') as fp:
        json.dump(rootCause, fp, indent=2)
if __name__ == "__main__":
    main()
