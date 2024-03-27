#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:v100:8
#SBATCH --mem 128G
#SBATCH -c 24
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Definitions
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
script1="train.py"
script2="evaluate.py"
data_dir_pre="$base_dir/data/lemur/train-pre"
data_dir_fine="$base_dir/data/lemur/train-fine"
model_dir_in="nccratliri/whisperseg-animal-vad"
model_dir_out="$base_dir/model/$(date +"%Y%m%d_%H%M%S")_j${SLURM_JOB_ID}_wseg-large"
output_dir="$base_dir/results"
output_identifier="large"

work_dir="/local/eckerlab/wseg_data"
job_dir="$work_dir/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script1%.*}"

epochs=6
batch_size=1

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
gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' ' ')
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
echo "[JOB] Moving data to cluster..."
mkdir -p "$job_dir"/data/{pretrain,finetune}
mkdir -p "$job_dir"/{pretrain_ckpt,finetune_ckpt}
cp -r "$data_dir_pre"/* "$job_dir/data/pretrain"
cp -r "$data_dir_fine"/* "$job_dir/data/finetune"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Pretraining..."
python "$code_dir/$script1" \
    --initial_model_path "$model_dir_in" \
    --train_dataset_folder "$job_dir/data/pretrain" \
    --model_folder "$job_dir/pretrain_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size

# Fine-tuning
echo "[JOB] Finetuning..."
python "$code_dir/$script1" \
    --initial_model_path "$job_dir/pretrain_ckpt/final_checkpoint" \
    --train_dataset_folder "$job_dir/data/finetune" \
    --model_folder "$job_dir/finetune_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size

# Evaluation
echo "[JOB] Evaluating..."
python "$code_dir/$script2" \
    -d "$job_dir/data/finetune" \
    -m "$job_dir/finetune_ckpt/final_checkpoint_ct2" \
    -o "$output_dir" \
    -i "$output_identifier"

# Move finished model to target job_dir
echo "[JOB] Moving trained model..."
mv "$job_dir/finetune_ckpt" "$model_dir_out"

# Clean up (already handled by trap)
