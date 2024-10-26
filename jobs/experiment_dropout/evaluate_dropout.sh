#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:RTX5000:1
#SBATCH --mem 64G
#SBATCH -c 8
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Definitions
model_name="$1"
cfg="$2"
base_dir="/usr/users/bhenne/projects/whisperseg"
experiment_dir="labels_moan_other"

code_dir="$base_dir"
script="evaluate.py"
data_tar="$base_dir/data/lemur_tar/lemur_data_cfg${cfg}.tar"
label_tar="$base_dir/data/lemur_tar/$experiment_dir/lemur_labels_cfg${cfg}_moan_other.tar"
model_dir="$model_name/final_checkpoint_ct2"
output_dir="$base_dir/results"
output_identifier="base_j${SLURM_JOB_ID}_moan_other"

work_dir="/local/eckerlab/wseg_data"
job_dir="$work_dir/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script%.*}"

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
    exit 1
}

# Trap SIGINT signal (Ctrl+C), ERR signal (error), and script termination
trap cleanup SIGINT ERR EXIT

# Prepare compute node environment
echo "[JOB] Preparing environment..."
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
echo "[JOB] Moving data to cluster..."
mkdir -p "$job_dir"
# tarballs contain directory structure for pretrain/finetune/test split
tar -xf "$data_tar" -C "$job_dir"
tar -xf "$label_tar" -C "$job_dir"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Evaluating checkpoint..."
python "$code_dir/$script" \
    --dataset_path "$job_dir/test" \
    --model_path "$model_dir" \
    --output_dir "$output_dir" \
    --identifier "$output_identifier"

# Clean up (already handled by trap)