#!/bin/bash

declare -A dict
dict["2.11.0"]="11.2"
dict["2.10.0"]="11.2"
dict["2.9.0"]="11.2"
dict["2.8.0"]="11.2"
dict["2.7.0"]="11.2"
dict["2.6.0"]="11.2"
dict["2.4.0"]="11.0"
dict["2.3.0"]="10.1"

declare -A tf2np
tf2np["2.11.0"]="1.24.2"
tf2np["2.10.0"]="1.24.2"
tf2np["2.9.0"]="1.24.2"
tf2np["2.8.0"]="1.24.2"
tf2np["2.7.0"]="1.24.2"
tf2np["2.6.0"]="1.21"
tf2np["2.4.0"]="1.21"
tf2np["2.3.0"]="1.21"

declare  -A pyversion
pyversion["2.11.0"]="3.10"
pyversion["2.10.0"]="3.10"
pyversion["2.9.0"]="3.10"
pyversion["2.8.0"]="3.10"
pyversion["2.7.0"]="3.9"
pyversion["2.6.0"]="3.9"
pyversion["2.4.0"]="3.7"
pyversion["2.3.0"]="3.7"

env_name=$1
tf_version=$2
library=$3

conda create --name $env_name python=${pyversion[$tf_version]} -y

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

pip install pandas
pip install ruamel-yaml==0.16.10
pip install scikit-learn==1.2.0
pip install networkx==2.4

cd /home/nimashiri/code/docter/
bash run_fuzzer.sh $library ./all_constr/tf2 ./configs/vi.config $tf_version | tee /home/workdir/ci.log


source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda deactivate

conda env remove --name $env_name -y