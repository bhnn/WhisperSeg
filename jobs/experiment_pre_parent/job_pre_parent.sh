#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:RTX5000:1
#SBATCH --mem 64G
#SBATCH -c 8
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

## CL parameters
# Check if the number of arguments passed is not exactly 1 or if config is empty
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <config_set>"
    echo "Error: Missing a required argument."
    exit 1
fi
cfg="$1"

# Definitions
base_dir="/usr/users/bhenne/projects/whisperseg"

code_dir="$base_dir"
experiment_dir="labels_pre_parent"
script1="train.py"
script2="evaluate.py"
data_tar="$base_dir/data/lemur_tar/data_pre_parent/lemur_data_cfg${cfg}_pre_parent.tar"
label_tar="$base_dir/data/lemur_tar/labels_pre_parent/lemur_labels_cfg${cfg}_pre_parent.tar"
model_dir_in="nccratliri/whisperseg-base-animal-vad"
model_dir_out="$base_dir/model/$(date +"%Y%m%d_%H%M%S")_j${SLURM_JOB_ID}_wseg-base_pre_parent"
output_dir="$base_dir/results"
output_identifier="base_j${SLURM_JOB_ID}_pre_parent"

work_dir="/local/eckerlab/wseg_data"
job_dir="$work_dir/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script1%.*}"
wandb_dir=$job_dir

# Model hyperparameter
project_name="wseg-lemur-results"
epochs=100
batch_size=4
learning_rate=8e-6
patience=10
val_ratio=0.1
wandb_notes="cfg${cfg}, rtx5000:1, tol0.5, bs${batch_size}, lr${learning_rate}, vratio${val_ratio}, pat${patience}"
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
gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' ' ')
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
echo "[JOB] Moving data to cluster..."
mkdir -p "$job_dir"/{pretrain_ckpt,pretrain2_ckpt,finetune_ckpt,wandb} # $job_dir itself + 4 others
# tarballs contain directory structure for pretrain/finetune/test split
tar -xf "$data_tar" -C "$job_dir"
tar -xf "$label_tar" -C "$job_dir"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Pretraining 1..."
python "$code_dir/$script1" \
    --initial_model_path "$model_dir_in" \
    --train_dataset_folder "$job_dir/pretrain" \
    --model_folder "$job_dir/pretrain_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --project $project_name \
    --run_name $SLURM_JOB_ID-0 \
    --run_notes "$wandb_notes" \
    --wandb_dir "$wandb_dir" \
    --validate_per_epoch 1 \
    --val_ratio $val_ratio \
    --save_per_epoch 1 \
    --patience $patience \
    --batch_size $batch_size \
    --learning_rate $learning_rate \
    --run_tags "base" "exp_parent"

# Pre-training, usually on multispecies wseg model
echo "[JOB] Pretraining 2..."
python "$code_dir/$script1" \
    --initial_model_path "$job_dir/pretrain_ckpt/final_checkpoint" \
    --train_dataset_folder "$job_dir/pretrain2" \
    --model_folder "$job_dir/pretrain2_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --project $project_name \
    --run_name $SLURM_JOB_ID-1 \
    --run_notes "$wandb_notes" \
    --wandb_dir "$wandb_dir" \
    --validate_per_epoch 1 \
    --val_ratio $val_ratio \
    --save_per_epoch 1 \
    --patience $patience \
    --batch_size $batch_size \
    --learning_rate $learning_rate \
    --run_tags "base" "exp_parent"

# Fine-tuning
echo "[JOB] Finetuning..."
python "$code_dir/$script1" \
    --initial_model_path "$job_dir/pretrain2_ckpt/final_checkpoint" \
    --train_dataset_folder "$job_dir/finetune" \
    --model_folder "$job_dir/finetune_ckpt" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --project $project_name \
    --run_name $SLURM_JOB_ID-2 \
    --run_notes "$wandb_notes" \
    --wandb_dir "$wandb_dir" \
    --validate_per_epoch 1 \
    --val_ratio $val_ratio \
    --save_per_epoch 1 \
    --patience $patience \
    --batch_size $batch_size \
    --learning_rate $learning_rate \
    --run_tags "base" "exp_parent"

# Evaluation
echo "[JOB] Evaluating..."
python "$code_dir/$script2" \
    -d "$job_dir/test" \
    -m "$job_dir/finetune_ckpt/final_checkpoint_ct2" \
    -o "$output_dir" \
    -i "$output_identifier"

# Move finished model to target job_dir
if [ -n "$(ls -A "$job_dir/finetune_ckpt")" ]; then
    echo "[JOB] Not moving trained model because of disk quota issues..."
    # mv "$job_dir/finetune_ckpt" "$model_dir_out"
fi

# Clean up (already handled by trap)