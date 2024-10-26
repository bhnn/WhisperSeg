#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:RTX5000:1
#SBATCH --mem 64G
#SBATCH -c 8
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Definitions
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
script="infer.py"
data_dir="$base_dir/data/inference/finetune"
model_dir="$base_dir/model/20240702_012658_j537476_wseg-base/final_checkpoint_ct2"
output_dir="$base_dir/data/inference/finetune"

majority_voting_trials=3

# Prevents excessive GPU memory reservation by Torch; enables batch sizes > 1 on v100s
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Prepare compute node environment
echo "[JOB] Preparing environment..."
module load anaconda3
source activate wseg

# Pre-training, usually on multispecies wseg model
echo "[JOB] Computing inference..."
python "$code_dir/$script" \
    --data_dir "$data_dir" \
    --model_path "$model_dir" \
    --output_dir "$output_dir" \
    --num_trials "$majority_voting_trials"

# Clean up (already handled by trap)
