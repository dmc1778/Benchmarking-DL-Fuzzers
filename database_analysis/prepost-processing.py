import pymongo
import os
import re
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

DB = pymongo.MongoClient(host="localhost", port=27017)["TF-Unique"]
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
Delete all documents in a collection based on the field source.
"""


def drop_document(dbname):
    mydb = myclient[dbname]
    for name in mydb.list_collection_names():
        print(name)
        mycol = mydb[name]
        mycol.delete_many({"source": "docs"})


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


def get_single_api(api, dbname):
    mydb = myclient[dbname]
    try:
        mydb.validate_collection(api)
        print("This collection exist")
    except pymongo.errors.OperationFailure:
        print("This collection doesn't exist")


def get_all_databases():
    print(myclient.list_database_names())


def get_overlap_docter(tool_name, libname):
    files = os.listdir(f"/home/nimashiri/code/docter/all_constr/{libname}")
    i = 0
    for api in files:
        api_split = api.split(".")
        new_api = ".".join(api_split[0:-1])
        flag = search_in_dataset(tool_name, new_api, libname)
        if flag:
            i = i + 1
            print(f"Found {new_api}:{i}")


def remove_overlap_docter(tool_name, libname):
    files = os.listdir(f"/home/nimashiri/Desktop/nima_constr/{libname}")
    i = 0
    for api in files:
        api_split = api.split(".")
        new_api = ".".join(api_split[0:-1])
        flag = search_in_dataset(tool_name, new_api, libname)
        if not flag:
            os.remove(
                os.path.join(f"/home/nimashiri/Desktop/nima_constr/{libname}", api)
            )
            i = i + 1
            print(f"Found non overlapping api{new_api}:{i}")


def search_in_dataset(tool_name, api_name, lib):
    flag = False
    if lib == "pt":
        data = pd.read_csv(
            "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/data/torch_data.csv"
        )
    else:
        data = pd.read_csv(
            "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/data/tf_data.csv"
        )
    for idx, row in data.iterrows():
        if api_name == row["Buggy API"]:
            flag = True
            # if lib == "pt":
            #     common_data_out = [
            #         tool_name,
            #         "torch",
            #         row["Issue link"],
            #         api_name,
            #         row["Release"],
            #     ]
            # else:
            #     common_data_out = [
            #         tool_name,
            #         "tf",
            #         row["Issue link"],
            #         api_name,
            #         row["Release"],
            #     ]
            # with open(
            #     "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/data/overlap_data_all.csv",
            #     mode="a",
            #     newline="\n",
            # ) as fd:
            #     writer_object = writer(fd)
            #     writer_object.writerow(common_data_out)
    return flag


def get_overlap_freefuzz(tool_name, dbname, lib):

    DB = pymongo.MongoClient(host="localhost", port=27017)[dbname]

    i = 0
    for api_name in DB.list_collection_names():
        flag = search_in_dataset(tool_name, api_name, lib)
        if flag:
            i = i + 1
            print(f"Found {api_name}:{i}")


def main():
    remove_overlap_docter("DocTer", "tf2")
    # get_overlap_freefuzz("mongo_based_tools", "deeprel-torch", "pt")
    # get_overlap_freefuzz("mongo_based_tools", "freefuzz-tf", "tf2")
    # get_overlap_docter("DocTer", "pt")
    # get_overlap_docter("DocTer", "tf2")


if __name__ == "__main__":
    main()
