#!/bin/bash

declare -A pyversion
pyversion["2.11.0"]="3.10"
pyversion["2.10.0"]="3.10"
pyversion["2.9.0"]="3.10"
pyversion["2.8.0"]="3.10"
pyversion["2.7.0"]="3.9"
pyversion["2.6.0"]="3.9"
pyversion["2.4.0"]="3.7"
pyversion["2.3.0"]="3.7"

env_name=$1
pt_version=$2
library=$3
setup_command=$4

conda create --name $env_name python=${pyversion[$pt_version]}   -y

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

$setup_command

pip install pandas
pip install ruamel-yaml==0.16.10
pip install scikit-learn==1.2.0
pip install networkx==2.4

cd /home/nimashiri/code/docter/
bash run_fuzzer.sh $library ./all_constr/pt ./configs/ci.config $pt_version | tee /home/workdir/ci.log

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda deactivate

conda env remove --name $env_name -y
