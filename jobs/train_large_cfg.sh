#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:v100:8
#SBATCH --mem 128G
#SBATCH -c 24
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Check if the number of arguments passed is not exactly 1 or if config is empty
if [ "$#" -ne 1 ] || [ -z "$1" ]; then
    echo "Usage: $0 <config_set> ([1-4], determines which config of data is used)"
    echo "Error: Config-set argument is empty or missing."
    exit 1
fi

# Definitions
cfg="$1"
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
script1="train.py"
script2="evaluate.py"
data_dir_pre="$base_dir/data/lemur_${cfg}/train-pre"
data_dir_fine="$base_dir/data/lemur_${cfg}/train-fine"
data_dir_test="$base_dir/data/lemur_${cfg}/test"
model_dir_in="nccratliri/whisperseg-animal-vad"
model_dir_out="$base_dir/model/$(date +"%Y%m%d_%H%M%S")_j${SLURM_JOB_ID}_wseg-large-cfg-$cfg"
output_dir="$base_dir/results"
output_identifier="large_cfg${cfg}"

work_dir="/local/eckerlab/wseg_data"
job_dir="$work_dir/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script1%.*}"

epochs=6
batch_size=8
wandb_notes="cfg${cfg}, 8x v100, bs${batch_size}, ep${epochs}"

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
}

# Trap SIGINT signal (Ctrl+C), ERR signal (error), and script termination
trap cleanup SIGINT ERR EXIT

# Prepare compute node environment
echo "[JOB] Preparing environment..."
gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' ' ')
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
echo "[JOB] Moving data to cluster..."
mkdir -p "$job_dir"/data/{pretrain,finetune,test}
mkdir -p "$job_dir"/{pretrain_ckpt,finetune_ckpt}
cp -r "$data_dir_pre"/* "$job_dir/data/pretrain"
cp -r "$data_dir_fine"/* "$job_dir/data/finetune"
cp -r "$data_dir_test"/* "$job_dir/data/test"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Pretraining..."
python "$code_dir/$script1" \
    --initial_model_path "$model_dir_in" \
    --train_dataset_folder "$job_dir/data/pretrain" \
    --model_folder "$job_dir/pretrain_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size \
    --run_name $SLURM_JOB_ID-0 \
    --run_notes "pretrain, ${wandb_notes}"

# Fine-tuning
echo "[JOB] Finetuning..."
python "$code_dir/$script1" \
    --initial_model_path "$job_dir/pretrain_ckpt/final_checkpoint" \
    --train_dataset_folder "$job_dir/data/finetune" \
    --model_folder "$job_dir/finetune_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size \
    --run_name $SLURM_JOB_ID-1 \
    --run_notes "finetune, ${wandb_notes}"

# Evaluation
echo "[JOB] Evaluating..."
python "$code_dir/$script2" \
    -d "$job_dir/data/test" \
    -m "$job_dir/finetune_ckpt/final_checkpoint_ct2" \
    -o "$output_dir" \
    -i "$output_identifier"

# Move finished model to target job_dir
echo "[JOB] Moving trained model..."
mv "$job_dir/finetune_ckpt" "$model_dir_out"

# Clean up (already handled by trap)
