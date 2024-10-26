#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:RTX5000:1
#SBATCH --mem 128G
#SBATCH -c 16
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Definitions
model_name="$1"
cfg="$2"
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
script="evaluate.py"
data_tar="$base_dir/data/lemur_tar/data_aug150/lemur_data_cfg${cfg}_aug150.tar"
label_tar="$base_dir/data/lemur_tar/labels_aug150/lemur_labels_cfg${cfg}_aug150.tar"
model_dir="$model_name/final_checkpoint_ct2"
output_dir="$base_dir/results"
output_identifier="$(date +"%Y%m%d_%H%M%S")_base_j${SLURM_JOB_ID}_aug150"

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

rm "$job_dir"/test/\(2021_04_21-19_04_26\)_ASWMUX209084_0000_first_PRED* # because random selection of 150 files accidentally included a file i hand-annotated
ls "$job_dir"/test/

# Pre-training, usually on multispecies wseg model
echo "[JOB] Evaluating checkpoint..."
python "$code_dir/$script" \
    --dataset_path "$job_dir/test" \
    --model_path "$model_dir" \
    --output_dir "$output_dir" \
    --identifier "$output_identifier"

# Clean up (already handled by trap)