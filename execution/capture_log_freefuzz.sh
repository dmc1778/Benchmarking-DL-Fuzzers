#!/bin/bash

lib=$1
source_version=$2
tool=$3
env_name=$4
dir_=$5
oracle=$6
api=$7
iteration=$8
fullAddr=$9

source /home/nimashiri/anaconda3/etc/profile.d/conda.sh
conda activate "$env_name"

CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib

output_file="/media/nimashiri/DATA/testing_results/tosem/$tool/$lib/$iteration/$source_version/$source_version.txt"
{ echo "Processing file: $fullAddr"; timeout 60s python "$fullAddr"; } |& tee -a "$output_file"

# ROOT_DIR="/media/nimashiri/DATA/testing_results/tosem/$tool/$lib/$iteration/$source_version/$dir_/$oracle/$api"
#log_directory="/media/nimashiri/DATA/testing_results/tosem/$tool/$lib/$iteration/$source_version"

# mkdir -p "$log_directory"

#touch "$log_directory$source_version.txt"

# output_file="/media/nimashiri/DATA/testing_results/tosem/$tool/$lib/$iteration/$source_version/$source_version.txt"


# find "$ROOT_DIR" -type f -name "*.py" | while read file
# do
#     trap "echo 'Process interrupted'; exit" SIGINT
#     { echo "Processing file: $file"; timeout 60s python "$file"; } |& tee -a "$output_file"
# done

# files=$(find "$ROOT_DIR" -type f -name "*.py")

# for file in $files; do
#     echo "Processing file: $file" timeout 60s python "$file" |& tee -a "$output_file"
#     # Check if the process was interrupted
#     if [ $? -eq 124 ]; then
#         echo "Timeout reached for $file"
#     fi
# done