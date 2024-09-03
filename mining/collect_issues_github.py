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
import csv
from openai import OpenAI
import backoff, time, openai
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

RETIRES = 10
CURRENT_TIME = datetime.datetime.now()

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

def find_matches(pattern, text):
    matches = pattern.findall(text)
    return matches if matches else None

def is_buggy(input_string):
    yes_variants = {"YES", "yes", "Yes"}
    return input_string in yes_variants

def match_label(labels):
    label_flag = False
    for l in labels:
        if "bug" in l["name"]:
            label_flag = True
    return label_flag

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completions_with_backoff(prompt, temperature,  model='gpt-4o-mini'):
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    return response

def stage_1_prompting(title, body):
    prompt_ = f"""
    You are a chatbot responsible for classifying a GitHub issue in deep learning libraries.
    Your task is to classify the following GitHub issue based on whether it is related to a deep learning API problem in [TensorFlow/PyTorch]. 
    The issue should involve specific API bugs, such as handling malicious input that causes logical and performance bugs, securitu vulnerabilities, incorrect output, or unexpected behavior.
    
    Please ignore any feature request or not implementation issues. 

    Please generate binary response, i.e., yes or no.

    Here is the issue title:
    Issue title: {title}

    Here is the issue body:
    Issue body: {body}
    
    Result: <your response>

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

def get_commits(
    githubUser,
    currentRepo,
    qm,
    page,
    amp,
    sh_string,
    last_com,
    page_number,
    branch_sha,
    potential_commits,
    current_token,
):

    page_number += 1

    print("Current page number is: {}".format(page_number))

    if page_number == 1:
        first_100_commits = (
            "https://api.github.com/repos/"
            + githubUser
            + "/"
            + currentRepo
            + "/issues"
            + qm
            + page
        )

        response = requests_retry_session().get(
            first_100_commits,
            headers={"Authorization": "token {}".format(current_token)},
        )
        link_ = first_100_commits
    else:
        response = requests_retry_session().get(
            last_com, headers={"Authorization": "token {}".format(current_token)}
        )
        link_ = last_com

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            link_,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            link_,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            link_,
            headers={"Authorization": "token {}".format(current_token)},
        )

    if response.status_code != 200:
        tokens_status[current_token] = False
        current_token = select_access_token(current_token)
        response = requests_retry_session().get(
            link_,
            headers={"Authorization": "token {}".format(current_token)},
        )

    first_100_commits = json.loads(response.text)

    if len(first_100_commits) == 1:
        return None
    for i, commit in enumerate(first_100_commits):
        title = commit['title'].lower()
        body = commit['body'].lower() if commit['body'] else ""
        
        memory_related_rules_strict = re.compile(
            r"(\bbottleneck\b|\bpoor\b|\bslow\b|\bweakness\b|\bdefect\b|\bbug\b|\berror\b|\binconsistent\b|\bincorrect\b|\bwrong\b|\bunexpected\b|\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
        )
        logical_bugs_rules = re.compile(
            r"(\bwrong result\b|\bunexpected output\b|\bunexpected result\b|\bincorrect calculation\b|\binconsistent behavior\b|\bunexpected behavior\b|\bincorrect logic\b|\bwrong calculation\b|\blogic error\b)"
        )
        performance_bugs_rules = re.compile(
            r"(\bmemory usage\b|\busage\b|\bslow\b|\bhigh CPU usage\b|\bhigh memory usage\b|\bpoor performance\b|\bslow response time\b|\bperformance bottleneck\b|\bperformance optimization\b|\bresource usage\b|\bbottleneck\b)"
        )

        match_flag = False
        
        if isinstance(commit["body"], str):
            memory_matches = find_matches(memory_related_rules_strict, title) or find_matches(memory_related_rules_strict, body)
            logical_matches = find_matches(logical_bugs_rules, title) or find_matches(logical_bugs_rules, body)
            performance_matches = find_matches(performance_bugs_rules, title) or find_matches(performance_bugs_rules, body)
           
            _date = commit["created_at"]
            sdate = _date.split("-")

            timestamp = datetime.datetime.strptime(_date, '%Y-%m-%dT%H:%M:%SZ')
            october_2023 = datetime.datetime(2023, 10, 31, 23, 59, 59)
            is_after_october_2023 = timestamp > october_2023

            if memory_matches:
                print(f"Memory-related issue found: {commit['html_url']}")
                print(f"Matched keywords: {memory_matches}")
                match_flag = True

            if logical_matches:
                print(f"Logical bug found: {commit['html_url']}")
                print(f"Matched keywords: {logical_matches}")
                match_flag = True
                
            if performance_matches:
                print(f"Performance bug found: {commit['html_url']}")
                print(f"Matched keywords: {performance_matches}")
                match_flag = True
                
            # gpt_response = stage_1_prompting(commit["title"], commit["body"])

            if match_flag and 'pull' not in commit['html_url']: #and is_buggy(gpt_response):
                if 'bug' in commit['body']:
                    label = 'bug'
                else:
                    label = 'no bug'
                _date = commit["created_at"]
                sdate = _date.split("-")

                with open(f"./issues/phase1/{currentRepo}.csv", "a", newline="\n", ) as fd:
                    writer_object = csv.writer(fd)
                    writer_object.writerow([currentRepo, commit["html_url"], commit["created_at"], label])

        if i == len(first_100_commits) - 1:
            if page_number == 53:
                print("here!")
            last_com = response.links["next"]["url"]

            potential_commits = []

            get_commits(
                githubUser,
                currentRepo,
                qm,
                page,
                amp,
                sh_string,
                last_com,
                page_number,
                branch_sha,
                potential_commits,
                current_token,
            )


def search_comit_data(c, commit_data):
    t = []

    for item in commit_data:
        temp = item.split("/")
        t.append("/" + temp[3] + "/" + temp[4] + "/")

    r_prime = c.split("/")
    x = "/" + r_prime[3] + "/" + r_prime[4] + "/"
    if any(x in s for s in t):
        return True
    else:
        return False


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


def main():

    repo_list = ["https://github.com/pytorch/pytorch"]

    if not os.path.exists("./issues"):
        os.makedirs("./issues")

    current_token = tokens[0]
    for lib in repo_list:
        x = []

        potential_commits = []

        r_prime = lib.split("/")

        qm = "?"
        page = "per_page=" + str(100)
        amp = "&"
        sh_string = "sha="

        branchLink = "https://api.github.com/repos/{0}/{1}/branches".format(
            r_prime[3], r_prime[4]
        )

        response = requests_retry_session().get(
            branchLink, headers={"Authorization": "token {}".format(current_token)}
        )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                branchLink, headers={"Authorization": "token {}".format(current_token)}
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                branchLink, headers={"Authorization": "token {}".format(current_token)}
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                branchLink, headers={"Authorization": "token {}".format(current_token)}
            )

        if response.status_code != 200:
            tokens_status[current_token] = False
            current_token = select_access_token(current_token)
            response = requests_retry_session().get(
                branchLink, headers={"Authorization": "token {}".format(current_token)}
            )

        branches = json.loads(response.text)

        selected_branch = random.choice(branches)
        branch_sha = selected_branch["commit"]["sha"]

        page_number = 0

        first_100_commits = (
            "https://api.github.com/repos/"
            + r_prime[3]
            + "/"
            + r_prime[4]
            + "/issues"
            + qm
            + page
        )

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

        if len(first_100_commits) >= 100:
            last_com = response.links["last"]["url"]

            get_commits(
                r_prime[3],
                r_prime[4],
                qm,
                page,
                amp,
                sh_string,
                last_com,
                page_number,
                branch_sha,
                potential_commits,
                current_token,
            )

        else:

            title = commit['title'].lower()
            body = commit['body'].lower() if commit['body'] else ""
            
            memory_related_rules_strict = re.compile(
                r"(\bbottleneck\b|\bpoor\b|\bslow\b|\bweakness\b|\bdefect\b|\bbug\b|\berror\b|\binconsistent\b|\bincorrect\b|\bwrong\b|\bunexpected\b|\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
            )
            logical_bugs_rules = re.compile(
                r"(\bwrong result\b|\bunexpected output\b|\bunexpected result\b|\bincorrect calculation\b|\binconsistent behavior\b|\bunexpected behavior\b|\bincorrect logic\b|\bwrong calculation\b|\blogic error\b)"
            )
            performance_bugs_rules = re.compile(
                r"(\bmemory usage\b|\busage\b|\bslow\b|\bhigh CPU usage\b|\bhigh memory usage\b|\bpoor performance\b|\bslow response time\b|\bperformance bottleneck\b|\bperformance optimization\b|\bresource usage\b|\bbottleneck\b)"
            )

            match_flag = False

            for i, commit in enumerate(first_100_commits):
                if isinstance(commit["body"], str):
                    
                    memory_matches = find_matches(memory_related_rules_strict, title) or find_matches(memory_related_rules_strict, body)
                    logical_matches = find_matches(logical_bugs_rules, title) or find_matches(logical_bugs_rules, body)
                    performance_matches = find_matches(performance_bugs_rules, title) or find_matches(performance_bugs_rules, body)
                                                
                    _date = commit["created_at"]
                    sdate = _date.split("-")
                    
                    if memory_matches:
                        print(f"Memory-related issue found: {commit['html_url']}")
                        print(f"Matched keywords: {memory_matches}")
                        match_flag = True

                    if logical_matches:
                        print(f"Logical bug found: {commit['html_url']}")
                        print(f"Matched keywords: {logical_matches}")
                        match_flag = True
                        
                    if performance_matches:
                        print(f"Performance bug found: {commit['html_url']}")
                        print(f"Matched keywords: {performance_matches}")
                        match_flag = True
                        
                    time.sleep(2)
                    # gpt_response = stage_1_prompting(commit["title"], commit["body"])

                    _date = commit["created_at"]
                    sdate = _date.split("-")
                    timestamp = datetime.datetime.strptime(_date, '%Y-%m-%dT%H:%M:%SZ')
                    october_2023 = datetime.datetime(2023, 10, 31, 23, 59, 59)
                    is_after_october_2023 = timestamp > october_2023
                    print(sdate[0])
                    # if True:
                    if match_flag and 'pull' not in commit['html_url']:
                            if 'bug' in commit['body']:
                                label = 'bug'
                            else:
                                label = 'no bug'
                            _date = commit["created_at"]
                            sdate = _date.split("-")

                            with open(
                                f"./issues/phase1/{r_prime[4]}.csv",
                                "a",
                                newline="\n",
                            ) as fd:
                                writer_object = csv.writer(fd)
                                writer_object.writerow(
                                    [
                                        r_prime[4],
                                        commit["html_url"],
                                        commit["created_at"],
                                        label
                                    ]
                                )
            potential_commits = []


if __name__ == "__main__":
    main()
