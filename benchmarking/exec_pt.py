import subprocess


TORCH_RELEASE_GPU = {
    "1.13.0": "pip install torch==1.13.0+cu117 --extra-index-url https://download.pytorch.org/whl/cu117",
    "1.12.0": "pip install torch==1.12.0+cu113 --extra-index-url https://download.pytorch.org/whl/cu113",
    "1.11.0": "pip install torch==1.11.0+cu113 --extra-index-url https://download.pytorch.org/whl/cu113",
    "1.10.1": "pip install torch==1.10.1+cu111 -f https://download.pytorch.org/whl/cu111/torch_stable.html",
    # "1.10.0": "conda install pytorch==1.10.0 torchvision==0.11.0 torchaudio==0.10.0 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    # "1.9.1": "conda install pytorch==1.9.1 torchvision==0.10.1 torchaudio==0.9.1 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    # "1.9.0": "conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    # "1.8.2": "conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia -y",
    # "1.8.1": "conda install pytorch==1.8.1 torchvision==0.9.1 torchaudio==0.8.1 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    # "1.8.0": "conda install pytorch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 cudatoolkit=11.1 -c pytorch -c conda-forge -y",
    # "1.7.1": "pip install torch==1.7.1",
    # "1.7.0": "pip install torch==1.7.0",
    # "1.6.0": "pip install torch==1.6.0",
    # "1.5.1": "pip install torch==1.5.1",
    # "1.5.0": "pip install torch==1.5.0",
    # "1.4.0": "pip install torch==1.4.0",
    # "1.1.0": "pip install torch==1.1.1",
    # "1.0.0": "pip install torch==1.1.0",
}


for pt_version, setup_command in reversed(TORCH_RELEASE_GPU.items()):

    env_name_pt = f"fuzzer_pt_{pt_version}"
    shell_command = [
        "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/benchmarking/setup_and_run_pt.sh",
        env_name_pt,
        pt_version,
        "torch",
        setup_command,
    ]
    subprocess.call(
        shell_command,
        shell=False,
    )

    print("")
