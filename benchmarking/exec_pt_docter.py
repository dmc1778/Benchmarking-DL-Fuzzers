import subprocess


TORCH_RELEASE_GPU = {
    "1.13.0": "conda install pytorch==1.13.0 torchvision==0.14.0 torchaudio==0.13.0 pytorch-cuda=11.7 -c pytorch -c nvidia -y",
    "1.12.0": "conda install pytorch==1.12.0 torchvision==0.13.0 torchaudio==0.12.0 cudatoolkit=11.6 -c pytorch -c conda-forge -y",
    "1.11.0": "conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch -y",
    "1.10.1": "conda install pytorch==1.10.1 torchvision==0.11.2 torchaudio==0.10.1 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    "1.10.0": "conda install pytorch==1.10.0 torchvision==0.11.0 torchaudio==0.10.0 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    "1.9.1": "conda install pytorch==1.9.1 torchvision==0.10.1 torchaudio==0.9.1 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    "1.9.0": "conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    "1.8.2": "conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia -y",
    "1.8.1": "conda install pytorch==1.8.1 torchvision==0.9.1 torchaudio==0.8.1 cudatoolkit=11.3 -c pytorch -c conda-forge -y",
    "1.8.0": "conda install pytorch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 cudatoolkit=11.1 -c pytorch -c conda-forge -y",
    "1.7.1": "conda install pytorch==1.7.1 torchvision==0.8.2 torchaudio==0.7.2 cudatoolkit=11.0 -c pytorch -y",
    "1.7.0": "conda install pytorch==1.7.0 torchvision==0.8.0 torchaudio==0.7.0 cudatoolkit=11.0 -c pytorch -y",
    "1.6.0": "conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.2 -c pytorch -y",
    "1.5.1": "conda install pytorch==1.5.1 torchvision==0.6.1 cudatoolkit=10.2 -c pytorch -y",
    "1.5.0": "conda install pytorch==1.5.0 torchvision==0.6.0 cudatoolkit=10.2 -c pytorch -y",
    "1.4.0": "conda install pytorch==1.4.0 torchvision==0.5.0 cudatoolkit=10.1 -c pytorch -y",
    "1.1.0": "conda install pytorch==1.1.0 torchvision==0.3.0 cudatoolkit=10.0 -c pytorch -y",
    "1.0.0": "conda install pytorch==1.1.0 torchvision==0.3.0 cudatoolkit=10.0 -c pytorch -y",
}


for pt_version, setup_command in TORCH_RELEASE_GPU.items():

    env_name_pt = f"fuzzer_docter_pt_{pt_version}"
    shell_command = [
        "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/benchmarking/setup_and_run_torch_docter.sh",
        env_name_pt,
        pt_version,
        "pytorch",
        setup_command,
    ]
    subprocess.call(
        shell_command,
        shell=False,
    )

    print("")
