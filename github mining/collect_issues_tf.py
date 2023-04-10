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
from mine_comments import parse_comment
import csv

# (0, nimashiri2012@gmail.com, 1, cse19922021@gmail.com, 2, nshiri@yorku.ca, 3, nshiri@cse.yorku.ca)
tokens = {
    0: "",
    1: "",
    2: "",
    3: "",
}

tokens_status = {
    "": True,
    "": True,
    "": True,
    "": True,
}


def match_label(labels):
    label_flag = False
    for l in labels:
        if "type:bug" in l["name"] or "prtype:bugfix" in l["name"]:
            label_flag = True
    return label_flag


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


retries = 10
now = datetime.datetime.now()


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

        memory_related_rules_strict = r"(\bbottleneck\b|\bpoor\b|\bbslow\b|\bweakness\b|\bdefect\b|\bbug\b|\berror\b\bbinconsistent\b|\bbincorrect\b|\bbwrong\b|\bbunexpected\b|\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
        title_match = False
        body_match = False

        if isinstance(commit["body"], str):
            if match_label(commit["labels"]):
                if re.findall(r"(tf\.)", commit["title"]) or re.findall(
                    r"(tf\.)", commit["body"]
                ):
                    comment_flag = parse_comment(commit["comments_url"], current_token)

                    if re.findall(memory_related_rules_strict, commit["title"]):
                        title_match = True
                    if re.findall(memory_related_rules_strict, commit["body"]):
                        body_match = True

                    tf_version = re.findall(r"(tf\s\d{1,2}[.]\d{1,2})", commit["body"])

                    _date = commit["created_at"]
                    sdate = _date.split("-")

                    if title_match or body_match or comment_flag:
                        _date = commit["created_at"]
                        sdate = _date.split("-")
                        print(
                            "Title status: {0}, Body status: {1}, Comment status: {2}".format(
                                title_match, body_match, comment_flag
                            )
                        )

                        with open(
                            f"./issues/{currentRepo}.csv",
                            "a",
                            newline="\n",
                        ) as fd:
                            writer_object = csv.writer(fd)
                            writer_object.writerow(
                                [
                                    currentRepo,
                                    commit["html_url"],
                                    commit["created_at"],
                                    tf_version,
                                ]
                            )

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

    repo_list = ["https://github.com/tensorflow/tensorflow"]

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

            memory_related_rules_strict = r"(\bbottleneck\b|\bpoor\b|\bbslow\b|\bweakness\b|\bdefect\b|\bbug\b|\berror\b\bbinconsistent\b|\bbincorrect\b|\bbwrong\b|\bbunexpected\b|\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
            logical_bugs_rules = r"(\bwrong result\b|\bunexpected output\b|\bunexpected result\b|\bincorrect calculation\b|\binconsistent behavior\b|\bunexpected behavior\b|\bincorrect logic\b|\bwrong calculation\b|\blogic error\b|)"
            performance_bugs_rules = r"(\bmemory usage\b|\busage\b|\bslow\b|\bhigh CPU usage\b|\bhigh memory usage\b|\bpoor performance\b|\bslow response time\b)|\bperformance bottleneck\b|\bperformance optimization\b|\bresource usage\b|\bbottleneck\b"

            title_match = False
            body_match = False

            for i, commit in enumerate(first_100_commits):
                if isinstance(commit["body"], str):
                    if match_label(commit["labels"]):
                        if re.findall(r"(tf\.)", commit["title"]) or re.findall(
                            r"(tf\.)", commit["body"]
                        ):
                            comment_flag = parse_comment(
                                commit["comments_url"], current_token
                            )
                            if re.findall(r"(tf\.)", commit["title"]) or re.findall(
                                r"(tf\.)", commit["body"]
                            ):
                                comment_flag = parse_comment(
                                    commit["comments_url"], current_token
                                )

                                if re.findall(
                                    memory_related_rules_strict, commit["title"]
                                ):
                                    title_match = True
                                if re.findall(
                                    memory_related_rules_strict, commit["body"]
                                ):
                                    body_match = True

                                _date = commit["created_at"]
                                sdate = _date.split("-")
                                tf_version = re.findall(
                                    r"(tf\s\d{1,2}[.]\d{1,2})", commit["body"]
                                )
                                print(sdate[0])
                                if title_match or body_match or comment_flag:
                                    _date = commit["created_at"]
                                    sdate = _date.split("-")

                                    with open(
                                        f"./issues/{r_prime[4]}.csv",
                                        "a",
                                        newline="\n",
                                    ) as fd:
                                        writer_object = csv.writer(fd)
                                        writer_object.writerow(
                                            [
                                                r_prime[4],
                                                commit["html_url"],
                                                commit["created_at"],
                                                tf_version,
                                            ]
                                        )
                    potential_commits = []


if __name__ == "__main__":
    main()
