#!/bin/bash

declare -A dict
dict["2.11.0"]="11.2"
dict["2.10.0"]="11.2"
dict["2.9.0"]="11.2"
dict["2.8.0"]="11.2"
dict["2.7.0"]="11.2"
dict["2.6.0"]="11.2"
dict["2.6.0"]="11.2"
dict["2.4.0"]="11.0"
dict["2.3.0"]="10.1"

env_name=$1
tf_version=$2
library=$3

conda create --name $env_name python=3.9 -y

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

conda install -c conda-forge cudatoolkit=${dict[$tf_version]} -y  
pip install nvidia-cudnn-cu11==8.6.0.163

CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib

pip install tensorflow==$tf_version
pip install protobuf==3.20.*

pip install pandas
pip install pymongo

python /media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/FreeFuzz/src/FreeFuzz.py --conf=/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/fuzzers/FreeFuzz/src/config/expr.conf --release=$tf_version --library=$library

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda deactivate

conda env remove --name $env_name -y

