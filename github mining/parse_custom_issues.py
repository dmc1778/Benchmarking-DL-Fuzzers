import pandas as pd
import json, sys
import os
import re
import requests
import random
import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from csv import writer
import csv
from openai import OpenAI
import backoff, time, openai
sys.path.insert(0, '/home/nima/repository/Benchmarking-DL-Fuzzers')
from utils.io import write_to_csv

tokens = {
    0: os.environ.get("TOKEN1"),
    1: os.environ.get("TOKEN2"),
    2: os.environ.get("TOKEN3"),
    3: os.environ.get("TOKEN4"),
}

tokens_status = {
    os.environ.get("TOKEN1"): True,
    os.environ.get("TOKEN2"): True,
    os.environ.get("TOKEN3"): True,
    os.environ.get("TOKEN4"): True,
}

def select_access_token(current_token):
    x = ""
    if all(value == False for value in tokens_status.values()):
        for k, v in tokens_status.items():
            tokens_status[k] = True

    for k, v in tokens.items():
        if tokens_status[v] != False:
            x = v
            break
    current_token = x
    return current_token


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def main(libname):
    current_token = tokens[0]
    
    data = pd.read_csv(f'issues/{libname}.csv')
    for idx, row in data.iterrows():
        issue_link = row.iloc[1]
        print(f"Issue::{idx}/{data.shape[0]}")
        issue_link = f"https://api.github.com/repos/{libname}/{libname}/issues/{issue_link.split('/')[-1]}"
        
        response = requests_retry_session().get(
            issue_link,
            headers={"Authorization": "token {}".format(issue_link)},
        )
        
        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                issue_link,
                headers={"Authorization": "token {}".format(current_token)},
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                issue_link,
                headers={"Authorization": "token {}".format(current_token)},
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                issue_link,
                headers={"Authorization": "token {}".format(current_token)},
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                issue_link,
                headers={"Authorization": "token {}".format(current_token)},
            )

        json_response = response.json()
        output_data = [libname, json_response["html_url"],json_response["created_at"], json_response['title'],]
        write_to_csv('issues', f'{libname}_detailed', output_data)

if __name__ == "__main__":
    # libname = sys.argv[1]
    main('tensorflow')