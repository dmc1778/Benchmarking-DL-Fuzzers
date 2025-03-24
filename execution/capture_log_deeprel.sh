#!/bin/bash

lib=$1
source_version=$2
tool=$3
env_name=$4
apiName=$5
iteration=$6

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib

output_file="/media/nimashiri/DATA/testing_results/icse26/$tool/$lib/$iteration/$source_version/expr/$source_version.txt"
{ echo "Processing file: $apiName"; timeout 60s python "$apiName"; } |& tee -a "$output_file"