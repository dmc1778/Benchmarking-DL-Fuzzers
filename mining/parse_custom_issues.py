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
from utils.fileUtils import write_to_csv

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

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

def is_buggy(input_string):
    yes_variants = {"YES", "yes", "Yes"}
    return input_string in yes_variants

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completions_with_backoff(prompt, temperature,  model='gpt-4o-mini'):
    response = client.chat.completions.create(
        model=model,
        logprobs=True,
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    return response

def issueIdentifier(title, body, libname):
    if libname == 'tensorflow':
        module_name = 'tf'
    else:
        module_name = 'torhc'
    prompt_ = f"""
    You are a chatbot responsible for classifying a GitHub issue in deep learning libraries.
    Your task is to classify the following GitHub issue based on whether it is related to a deep learning API problem in {libname}. 
    
    Inclusion criteria:
    1. The issue is related to a bug that is arising from the usage {libname} APIs.
    2. The issue can be from one sigle torch API call or usage of multiple torch APIs together.
    3. APIs always start with {module_name}.API_NAME.
    4. The issue has a minimum reproducing example code in Python language.
    5. The issue can be replicated in Linux OS.
    6. The issue can be replicated on Nvidia GPUs.
    7. The issue is related to Python front-end.

    Exclusion criteria:
    1. Ignore issues related to feature request or feature shortcoming. 
    2. Ignore Not implementation errors.

    Please generate YES or NO response.
    
    Here is the issue title:
    Issue title: {title}

    Here is the issue body:
    Issue body: {body}
    
    <output>

    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

def extractAPIName(title, body, libname):
    if libname == 'tensorflow':
        module_name = 'tf'
    else:
        module_name = 'torhc'
    prompt_ = f"""
    Extract the name of the API(s) mentioned in the following GitHub issue
    body or title that are reported to cause the bug in {libname}:

    REMEMBER APIs always start with {module_name}.API_NAME.
    
    Here is the issue title:
    Issue title: {title}

    Here is the issue body:
    Issue body: {body}
    
    Generate the API Name without any additional explanation.
    <API Name>

    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

def extractVersion(title, body, libname):
    prompt_ = f"""
    Identify the version of {libname} that is reported to be affected 
    by the bug in the following GitHub issue description:
    
    Please only extract the following versions for PyTorch:
    2.0.0, 2.0.1, 2.1.0
    Please only extract the following versions for TensorFlow:
    2.11.0, 2.12.0, 2.13.0, 2.14.0

    Here is the issue description:
    Issue body: {body}
    
    Generate the version number without any additional explanation.
    <Library Version>

    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

def cudaVersion(title, body, libname):
    prompt_ = f"""
    Identify the CUDA version mentioned in the following GitHub issue description:

    Here is the issue title:
    Issue title: {title}

    Here is the issue body:
    Issue body: {body}

    Provide only the CUDA version(s) referenced in the description.
    <CUDA version>
    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

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
    
    data = pd.read_csv(f'issues/phase1/{libname}.csv')
    for idx, row in data.iterrows():
        # if not row['Related Checks']:
        #     print('This issue is already labeled as not related.')
        #     continue
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

        if re.findall(r'(2\.11\.0|2\.12\.0|2\.13\.0|2\.14\.0)', json_response["body"]):
        #if re.findall(r'(PyTorch|torch)\s+version:\s*(2\.0\.0|2\.0\.1|2\.1\.0|2\.11\.0|2\.12\.0|2\.13\.0|2\.14\.0)(\+\S*)?|torch==\s*(2\.0\.0|2\.0\.1|2\.1\.0|2\.11\.0|2\.12\.0|2\.13\.0|2\.14\.0)', json_response["body"]):
            bug_label = issueIdentifier(json_response["title"], json_response["body"], libname)
            if is_buggy(bug_label):
                api_name = extractAPIName(json_response["title"], json_response["body"], libname)
                lib_version = extractVersion(json_response["title"], json_response["body"], libname)
                cuda_version = cudaVersion(json_response["title"], json_response["body"], libname)
                print(lib_version)
                #if libname == 'pytorch' and lib_version in ['2.0.0', '2.0.1', '2.1.0'] or libname == 'tensorflow' and lib_version in ['2.11.0', '2.12.0', '2.13.0', '2.14.0']:
                output_data = [libname, json_response["html_url"],json_response["created_at"], json_response['title'], bug_label, api_name, lib_version, cuda_version]
                write_to_csv('issues/phase2', f'{libname}', output_data)
        else:
            print('This is not a valid bug version!')

if __name__ == "__main__":
    libname = sys.argv[1]
    main(libname)
    # main('pytorch')