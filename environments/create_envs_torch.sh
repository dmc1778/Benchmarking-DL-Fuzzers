#!/bin/bash

env_names=("torch_1.13.0" "torch_2.0.0" "torch_2.0.1" "torch_2.1.0" "torch_2.2.0")

declare -A torchVersions
torchVersions["torch_1.13.0"]="pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 torchaudio==0.13.0 --extra-index-url https://download.pytorch.org/whl/cu117"
torchVersions["torch_2.0.0"]="pip install torch==2.0.0 torchvision==0.15.1 torchaudio==2.0.1 --index-url https://download.pytorch.org/whl/cu118"
torchVersions["torch_2.0.1"]="pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118"
torchVersions["torch_2.1.0"]="pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118"
torchVersions["torch_2.2.0"]="pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118"

for env_name in "${env_names[@]}"; do
    echo "Creating conda environment: $env_name"

    conda create --name "$env_name" python=3.9 -y 

    source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
    conda activate "$env_name"

    conda install -c conda-forge cudatoolkit=11.8 -y 
    pip install nvidia-cudnn-cu11==8.6.0.163
    CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib

    ${torchVersions[$env_name]}

    # pip install pymongo
    # pip install textdistance
    # pip install munkres 
    pip install protobuf==3.20.*
    pip install numpy==1.22.4
    pip install pandas
    # pip install configparser
    # pip install termcolor
    # pip install pathlib 
    # pip install ruamel-yaml 
    # pip install scikit-learn 
    # pip install networkx
    # pip install openai
    # pip install astunparse==1.6.3
    # pip install transformers==4.26.0
    # pip install sysv-ipc
    # pip install z3-solver
    conda deactivate

    echo "Completed setup for: $env_name"
done