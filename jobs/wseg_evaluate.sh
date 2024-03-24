#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:rtx5000:1
#SBATCH --mem 128G
#SBATCH -c 32
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Define paths
base="/usr/users/bhenne/projects/whisperseg"
code="$base"
script="evaluate.py"
data="$base/data/lemur_snippet_1/train"
model="$base/model/whisperseg-lemur-finetuned-snip1/final_checkpoint_ct2"
output="$base/results"
work="/local/eckerlab/wseg_data"

# Prepare modules and conda environment for compute node
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
destination="$work/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script%.*}"
mkdir -p "$destination"
cp -r "$data"/* "$destination"

# Run script || true, ensuring cleanup even on failure
python "$code/$script" \
    --dataset_path "$destination" \
    --model_path "$model" \
    --output_dir "$output" \
    || true

# Clean up: remove data, "<time>_<job>/" directory and parent directory, if empty
rm -rf "$destination"
if [ -z "$(ls -A "${destination%/*}")" ]; then
    rmdir "${destination%/*}"
fi
