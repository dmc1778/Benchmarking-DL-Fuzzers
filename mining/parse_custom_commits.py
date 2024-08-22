from csv import writer
import os, subprocess, re, csv
from git import Repo
from datetime import datetime
from datetime import datetime, timezone
from openai import OpenAI
import backoff, time
import openai, sys
import tiktoken
import pandas as pd
from pydriller import Repository
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get(".env")
)

THIS_PROJECT = os.getcwd()

def is_buggy(input_string):
    yes_variants = {"YES", "yes", "Yes"}
    return input_string in yes_variants

def write_list_to_txt4(data, filename):
    with open(filename, "a", encoding='utf-8') as file:
        file.write(data+'\n')
        
def no_matches_in_commit(commit_message, patterns):
    for pattern in patterns:
        if re.findall(pattern, commit_message):
            return True 
    return False


def save_commit(data, owner, libname, phase, mode='stat'):
    if not os.path.exists(f'commits/{owner}/{phase}'):
        os.makedirs(f'commits/{owner}/{phase}')

    fname = f"commits/{owner}/{phase}/{libname}_{mode}.csv"
    with open(fname,"a", newline="\n",) as fd:
        writer_object = csv.writer(fd)
        writer_object.writerow(data)

def read_txt(fname):
    with open(fname, "r") as fileReader:
        data = fileReader.read()
    return data

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

def commitIdentifier(message, libname):
    if libname == 'tensorflow':
        module_name = 'tf'
    else:
        module_name = 'torhc'
    prompt_ = f"""
    You are a chatbot responsible for classifying a GitHub commit in deep learning libraries.
    Your task is to classify the following commit based on whether it is fixing
    a bug that is arising from the usage of {libname} user API(s). 
    
    Inclusion criteria:
    1. The commit is fixing a bug that is arising from the usage {libname} user API(s).
    2. The commit is fixing a sigle {libname} API call or usage of multiple {libname} APIs together.
    3. API(s) always start with {module_name}.API_NAME.

    Exclusion criteria:
    1. Ignore commits that address feature request or feature shortcoming. 

    Please generate YES or NO response.
    
    Here is the commit message:
    Commit message: {message}
    
    <output>

    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

def extractAPIName(message, libname):
    if libname == 'tensorflow':
        module_name = 'tf'
    else:
        module_name = 'torhc'
    prompt_ = f"""
    Extract the name of the API(s) mentioned in the following commit message
    that are reported to cause the bug in {libname}:

    REMEMBER APIs always start with {module_name}.API_NAME.
    
    Here is the commit message:
    Commit message: {message}
    
    Generate the API Name without any additional explanation.
    <API(s) Name>

    """
    response = completions_with_backoff(prompt_, 0.7)
    return response.choices[0].message.content

def get_token_count(string):

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    num_tokens = len(encoding.encode(string))

    return num_tokens

def main(owner, repo_name, phase):
    data = pd.read_csv(f'commits/{owner}/two/{repo_name}_main.csv')
    
    if phase == 'one':
        memory_related_rules_strict = r"(\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
        logical_bugs_rules = r"(\bweakness\b|\bdefect\b|\bbug\b|\berror\b|\binconsistent\b|\bincorrect\b|\bwrong\b|\bunexpected\b|\bwrong result\b|\bunexpected output\b|\bunexpected result\b|\bincorrect calculation\b|\binconsistent behavior\b|\bunexpected behavior\b|\bincorrect logic\b|\bwrong calculation\b|\blogic error\b)"
        performance_bugs_rules = r"(\bmemory usage\b|\busage\b|\bslow\b|\bhigh CPU usage\b|\bhigh memory usage\b|\bpoor performance\b|\bslow response time\b|\bperformance bottleneck\b|\bperformance optimization\b|\bresource usage\b|\bbottleneck\b)"
    if phase == 'two':
        issue_pattern = r"\b(?:fixes|fixing|fix|fixed|fixed|closes|resolves|related to|refs|#|gh-)\s*#?(\d+)"
        api_pattern = r"tf\.[a-zA-Z0-9_]+\b|torch\.[a-zA-Z0-9_]+\b"
    #api_name_match = r"(\btf\.[a-zA-Z0-9_]+\b|\btorch\.[a-zA-Z0-9_]+\b)"
    # 
    
    try:
        temp = []
        for i, row in data.iterrows():
                print(f"Analyzed commits: {i}/{len(data)}")
                full_link = row.iloc[0].split('/')[-1]
                if repo_name == 'tensorflow' or repo_name == 'pytorch':
                    repository_path = THIS_PROJECT+'/ml_repos/'+owner
                    
                v = f"https://github.com/{owner}/{repo_name}.git"

                if not os.path.exists(repository_path):
                    subprocess.call('git clone '+v+' '+repository_path, shell=True)
            
                for commit in Repository(f"ml_repos/{repo_name}/{repo_name}", single=full_link).traverse_commits():
                        if phase == 'one':
                            _match1 = re.findall(memory_related_rules_strict, commit.msg)
                            _match2 = re.findall(logical_bugs_rules, commit.msg)
                            _match3 = re.findall(performance_bugs_rules, commit.msg)
                                    
                            sec_flag = logic_flag = perf_flag = False
                            if _match1:
                                sec_flag = True
                            elif _match2:
                                logic_flag = True
                            elif _match3:
                                perf_flag = True
                            else:
                                pass  
                                
                        if phase == 'two':
                            _match4 = re.findall(issue_pattern, commit.msg)
                            _match5 = re.findall(api_pattern, commit.msg)

                        if phase == 'one':
                            if _match1 or _match2 or _match3:
                                stat = [full_link, str(sec_flag), str(logic_flag), str(perf_flag)]
                                save_commit(stat, owner, repo_name, phase, 'stat')
                                        
                                commit_date = commit.author_date.year
                                data = [row.iloc[0], commit_date]
                                save_commit(data, owner, repo_name, phase, 'main')
                        if phase == 'three':
                            bug_label = commitIdentifier(commit.msg, repo_name)
                            if is_buggy(bug_label):
                                apiName = extractAPIName(commit.msg, repo_name)
                                commit_date = commit.author_date.year
                                data = [row.iloc[0], commit_date, apiName]
                                save_commit(data, owner, repo_name, phase, 'main')
                        else:
                            if _match4 or _match5:
                                commit_date = commit.author_date.year
                                data = [row.iloc[0], commit_date]
                                save_commit(data, owner, repo_name, phase, 'main')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    owner = sys.argv[1]
    repo_name = sys.argv[2]
    phase_one = sys.argv[3]
    # library_name = 'pytorch'
    main(owner, repo_name, phase_one)
    # main('pytorch', 'pytorch', 'two')