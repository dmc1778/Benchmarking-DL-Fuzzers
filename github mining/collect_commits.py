from csv import writer
import os, subprocess, re, csv
from git import Repo
from datetime import datetime
from datetime import datetime, timezone
from openai import OpenAI
import backoff, time
import openai, sys
import tiktoken
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get(".env")
)

THIS_PROJECT = os.getcwd()

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
def completions_with_backoff(prompt, model='gpt-4-0125-preview'):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    return response

def stage_1_prompting(item, libname):
    prompt_ = f"""
    You are a chatbot responsible for classifying a commit message that fixing bugs in {libname} backend implementation.
    Your task is to classify if the commit is fixing an improper/missing validation/checker bug. Please generate binary response, i.e., yes or no.

    Here is the commit message:
    Commit message: {item}

    Result: <your response>

    """

    return prompt_

def stage_2_prompting(item, libname):
    prompt_ = f"""
    You are a chatbot responsible for analyzing a commit message that fixing bugs in {libname} backend implementation.
    Your task is to perform analysis on the bug fixing commit that fixing an improper/missing validation/checker bug.

    Here is the commit message:
    Commit message: {item}
    
    Your analysis should contain the following factors:

    Root cause: <What is the root cause of the bug>
    Impact of the bug: <what is the impact of the bug>
    Fixing pattern: <how the bug is fixed>

    Please generate a short response for each factor. 
    Result: <your response>

    """

    return prompt_

def get_token_count(string):

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    num_tokens = len(encoding.encode(string))

    return num_tokens

def main(owner, repo_name, phase):
    # owner = 'google'
    # repo_name = 'jax'
    REPO_LIST = [f"https://github.com/{owner}/{repo_name}"]
    r_prime = REPO_LIST[0].split("/")

    v = REPO_LIST[0] + ".git"

    if not os.path.exists(
        THIS_PROJECT + "/ml_repos/" + r_prime[3] + "/" + r_prime[4]
    ):
        subprocess.call(
            "git clone "
            + v
            + " "
            + THIS_PROJECT
            + "/ml_repos/"
            + r_prime[3]
            + "/"
            + r_prime[4],
            shell=True,
        )

    r = Repo(THIS_PROJECT + "/ml_repos/" + r_prime[3] + "/" + r_prime[4])

    # subprocess.check_call(
    #     "./mining/checkout.sh %s "
    #     % (THIS_PROJECT + "/ml_repos_cloned/" + r_prime[3] + "/" + r_prime[4]),
    #     shell=True,
    # )

    subprocess.run("./mining/checkout.sh", shell=True)

    hisotry_file = f'logs/{r_prime[3]}_parsed_commits.txt'

    if not os.path.exists(hisotry_file):
        f1 = open(hisotry_file, 'a')

    if r_prime[3] == 'pytorch':
        max_count = 69389
        branch_name = 'main'
    elif r_prime[3] == 'google':
        max_count = 22127
        branch_name = 'main'
    else:
        max_count = 159725
        branch_name = "master"

    all_commits = list(r.iter_commits(branch_name, max_count=max_count))
    hist = read_txt(f'logs/{r_prime[3]}_parsed_commits.txt')

    if phase == 'one':
        memory_related_rules_strict = r"(\bdenial of service\b|\bDOS\b|\bremote code execution\b|\bCVE\b|\bNVD\b|\bmalicious\b|\battack\b|\bexploit\b|\bRCE\b|\badvisory\b|\binsecure\b|\bsecurity\b|\binfinite\b|\bbypass\b|\binjection\b|\boverflow\b|\bHeap buffer overflow\b|\bInteger division by zero\b|\bUndefined behavior\b|\bHeap OOB write\b|\bDivision by zero\b|\bCrashes the Python interpreter\b|\bHeap overflow\b|\bUninitialized memory accesses\b|\bHeap OOB access\b|\bHeap underflow\b|\bHeap OOB\b|\bHeap OOB read\b|\bSegmentation faults\b|\bSegmentation fault\b|\bseg fault\b|\bBuffer overflow\b|\bNull pointer dereference\b|\bFPE runtime\b|\bsegfaults\b|\bsegfault\b|\battack\b|\bcorrupt\b|\bcrack\b|\bcraft\b|\bCVE-\b|\bdeadlock\b|\bdeep recursion\b|\bdenial-of-service\b|\bdivide by 0\b|\bdivide by zero\b|\bdivide-by-zero\b|\bdivision by zero\b|\bdivision by 0\b|\bdivision-by-zero\b|\bdivision-by-0\b|\bdouble free\b|\bendless loop\b|\bleak\b|\binitialize\b|\binsecure\b|\binfo leak\b|\bnull deref\b|\bnull-deref\b|\bNULL dereference\b|\bnull function pointer\b|\bnull pointer dereference\b|\bnull-ptr\b|\bnull-ptr-deref\b|\bOOB\b|\bout of bound\b|\bout-of-bound\b|\boverflow\b|\bprotect\b|\brace\b|\brace condition\b|RCE|\bremote code execution\b|\bsanity check\b|\bsanity-check\b|\bsecurity\b|\bsecurity fix\b|\bsecurity issue\b|\bsecurity problem\b|\bsnprintf\b|\bundefined behavior\b|\bunderflow\b|\buninitialize\b|\buse after free\b|\buse-after-free\b|\bviolate\b|\bviolation\b|\bvsecurity\b|\bvuln\b|\bvulnerab\b)"
        logical_bugs_rules = r"(\bweakness\b|\bdefect\b|\bbug\b|\berror\b|\binconsistent\b|\bincorrect\b|\bwrong\b|\bunexpected\b|\bwrong result\b|\bunexpected output\b|\bunexpected result\b|\bincorrect calculation\b|\binconsistent behavior\b|\bunexpected behavior\b|\bincorrect logic\b|\bwrong calculation\b|\blogic error\b)"
        performance_bugs_rules = r"(\bmemory usage\b|\busage\b|\bslow\b|\bhigh CPU usage\b|\bhigh memory usage\b|\bpoor performance\b|\bslow response time\b|\bperformance bottleneck\b|\bperformance optimization\b|\bresource usage\b|\bbottleneck\b)"
    if phase == 'two':
        issue_pattern = re.compile(r"\b(?:fixes|fixing|fix|fixed|fixed|closes|resolves|related to|refs|#|gh-)\s*#?(\d+)", re.IGNORECASE)
    
    #api_name_match = r"(\btf\.[a-zA-Z0-9_]+\b|\btorch\.[a-zA-Z0-9_]+\b)"
    # 
    
    try:
        temp = []
        for i, com in enumerate(all_commits):
                com.diff
                if com.hexsha not in hist:
                    commit_link = REPO_LIST[0] + "/commit/" + com.hexsha 
                    write_list_to_txt4(com.hexsha, f'logs/{r_prime[3]}_parsed_commits.txt')
                    _date = datetime.fromtimestamp(com.committed_date)
                    
                    if phase == 'one':
                        _match1 = re.findall(memory_related_rules_strict, com.message)
                        _match2 = re.findall(logical_bugs_rules, com.message)
                        _match3 = re.findall(performance_bugs_rules, com.message)
                        
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
                        _match4 = re.findall(issue_pattern, com.message)
                    
                    print("Analyzed commits: {}/{}".format(i, len(all_commits)))

                    parent = com.parents[0]
                    
                    diffs  = {
                        diff.a_path: diff for diff in com.diff(parent)
                    }
                    # if len(diffs) == 1:
                    file_name = list(diffs.keys())
                    if len(file_name) == 1:
                        if 'test' in file_name or 'tests' in file_name:
                            print('this change is related to tests, so I am ignoring it.')
                            continue
                            # if no_matches_in_commit(com.message, patterns):
                    if phase == 'one':
                        if _match1 or _match2 or _match3:
                            stat = [commit_link, str(sec_flag), str(logic_flag), str(perf_flag)]
                            save_commit(stat, owner, repo_name, phase, 'stat')
                    
                                # with open(f"commits/{r_prime[3]}.txt", "w") as file:
                                #     file.write(f"Security related Bugs:{sec_count}" + "\n")
                                #     file.write(f"Logical Bugs:{logic_count}" + "\n")
                                #     file.write(f"Performance Bugs:{perf_count}" + "\n")
                                            # prompt_ = stage_2_prompting(com.message, r_prime[3])
                                            # t_count = get_token_count(prompt_)
                                            # if t_count <= 4097:
                                            #     time.sleep(3)
                                            #     conversations = completions_with_backoff(prompt_)
                                            #     decision = conversations.choices[0].message.content
                                            #     decision_split = decision.split('\n')
                                            #     filtered_list = list(filter(None, decision_split))

                                
                            commit_date = com.committed_date
                            dt_object = datetime.fromtimestamp(commit_date)
                            commit_date = dt_object.replace(tzinfo=timezone.utc)
                            # print(commit_date.year)
                            #if commit_date.year > 2016:
                            data = [commit_link, commit_date.strftime("%Y-%m-%d")]
                            save_commit(data, owner, repo_name, phase, 'main')
                    else:
                        if _match4:
                            commit_date = com.committed_date
                            dt_object = datetime.fromtimestamp(commit_date)
                            commit_date = dt_object.replace(tzinfo=timezone.utc)
                            # print(commit_date.year)
                            #if commit_date.year > 2016:
                            data = [commit_link, commit_date.strftime("%Y-%m-%d")]
                            save_commit(data, owner, repo_name, phase, 'main')
                else:
                    print('This commit has been already analyzed!')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    owner = sys.argv[1]
    repo_name = sys.argv[2]
    phase_one = sys.argv[3]
    # library_name = 'pytorch'
    main(owner, repo_name, phase_one)
    # main('pytorch', 'pytorch')