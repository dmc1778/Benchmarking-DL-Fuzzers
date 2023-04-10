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
pip install textdistance
pip install munkres
pip install tensorflow

python /media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/DeepREL/pytorch/src/DeepREL.py $pt_version $library

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda deactivate

conda env remove --name $env_name -y
