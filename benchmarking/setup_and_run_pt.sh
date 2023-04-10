#!/bin/bash

env_name=$1
pt_version=$2
library=$3
setup_command=$4

conda create --name $env_name python=3.9 -y

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

$setup_command

pip install pandas
pip install pymongo

pip install tensorflow
conda install pytorch==1.12.0 torchvision==0.13.0 torchaudio==0.12.0 cudatoolkit=11.6 -c pytorch -c conda-forge -y

python /media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/FreeFuzz/src/FreeFuzz.py --conf=/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/FreeFuzz/src/config/expr.conf --release=$pt_version --library=$library

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda deactivate

conda env remove --name $env_name -y

conda clean --all -y