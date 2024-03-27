#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:v100:1
#SBATCH --mem 128G
#SBATCH -c 24
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Definitions
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
script1="infer.py"
data_dir="$base_dir/data/inference"
model_dir="$base_dir/model/<model_name>/final_checkpoint_ct2"
output_dir="$base_dir/results"

work_dir="/local/eckerlab/wseg_data"
job_dir="$work_dir/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script1%.*}"

# Prevents excessive GPU memory reservation by Torch; enables batch sizes > 1 on v100s
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Function executes: on script exit, on error, on manual termination with ctrl-c
cleanup() {
    if [ -z "$cleanup_done" ]; then # otherwise cleanup runs twice for SIGINT or ERR
        cleanup_done=true
        echo "[JOB] Cleaning up..."
        # Clean up: remove data, "<time>_<id>_<job>/" directory and parent working directory, if empty
        rm -rf "$job_dir"
        if [ -z "$(ls -A "${job_dir%/*}")" ]; then
            rmdir "${job_dir%/*}"
        fi
        unset PYTORCH_CUDA_ALLOC_CONF
    fi
    exit $1
}

# Trap SIGINT signal (Ctrl+C), ERR signal (error), and script termination
trap 'cleanup 1' SIGINT
trap 'cleanup 1' ERR
trap 'cleanup 0' EXIT

# Prepare compute node environment
echo "[JOB] Preparing environment..."
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
echo "[JOB] Moving data to cluster..."
mkdir -p "$job_dir"/data
cp -r "$data_dir"/* "$job_dir/data"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Computing inference..."
python "$code_dir/$script" \
    --data_dir "$job_dir/data" \
    --model_path "$model_dir" \
    --output_dir "$output_dir"

# Clean up (already handled by trap)
