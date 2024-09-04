import pymongo
import os
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


def get_overlap_docter(libname):
    files = os.listdir(f"/home/nima/code/docter/all_constr/{libname}")
    i = 0
    for api in files:
        dst_path = os.path.join(f"/home/nima/code/docter/all_constr/{libname}", api)
        api_split = api.split(".")
        new_api = ".".join(api_split[0:-1])
        flag = search_in_dataset(new_api, libname)
        if flag:
            if not os.path.exists(f'/home/nima/code/docter/nima_constr/{libname}'):
                os.makedirs(f'/home/nima/code/docter/nima_constr/{libname}')
            shutil.copy(dst_path, f'/home/nima/code/docter/nima_constr/{libname}')
                


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
    if lib == "pt":
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
    return flag


def get_overlap_freefuzz(tool_name, dbname, lib):

    DB = pymongo.MongoClient(host="localhost", port=27017)[dbname]

    i = 0
    for api_name in DB.list_collection_names():
        flag = search_in_dataset(tool_name, api_name, lib)
        if flag:
            i = i + 1
            print(f"Found {api_name}:{i}")


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

def remove_non_overlap_mongodb(libname):
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
            drop_document(api_name, libname)
        

def main():    
    # get_overlap_docter('tf2')
    # remove_non_overlap_mongodb('tf')


if __name__ == "__main__":
    main()
