import json
import os
import re
import requests
import random
import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from csv import writer

tokens = {
    0: "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",
    1: "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",
    2: "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",
    3: "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",
}

tokens_status = {
    "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": True,
    "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": True,
    "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": True,
    "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": True,
}

memory_related_rules_strict = r"(\bbottleneck\b|\bpoor\b|\bbslow\b|\bweakness\b|\bdefect\b|\bbug\b|\berror\b\bbinconsistent\b|\bbincorrect\b|\bbwrong\b|\bbunexpected\b|\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"


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


def parse_comment(first_100_commits, current_token):
    match_flag = False
    response = requests_retry_session().get(
        first_100_commits,
        headers={"Authorization": "token {}".format(current_token)},
    )
    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            first_100_commits,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            first_100_commits,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            first_100_commits,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            first_100_commits,
            headers={"Authorization": "token {}".format(current_token)},
        )

    first_100_commits = json.loads(response.text)

    if first_100_commits:
        try:
            for i, com in enumerate(first_100_commits):

                body_match_sec = re.findall(memory_related_rules_strict, com["body"])

                if body_match_sec:
                    match_flag = True
        except Exception as e:
            print(e)

    return match_flag
