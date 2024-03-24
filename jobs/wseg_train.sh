#!/bin/bash

# SLURM directives
#SBATCH --gres=gpu:rtx5000:2
#SBATCH --mem 128G
#SBATCH -c 32
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

# Define paths
base="/usr/users/bhenne/projects/whisperseg"
code="$base"
script1="train.py"
script2="evaluate.py"
data_pre="$base/data/lemur_snippet_1/train"
data_fine="$base/data/lemur_snippet_1/train"
model_in="nccratliri/whisperseg-base-animal-vad"
model_out="$base/model/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_wseg-lemur"
work="/local/eckerlab/wseg_data"
output="$base/results"
output_identifier="cfg1"

epochs=6
batch_size=4

# Prepare compute node environment
gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' ' ')
module load anaconda3
source activate wseg

# Create temporary job directory and copy data
destination="$work/$(date +"%Y%m%d_%H%M%S")_${SLURM_JOB_ID}_${script1%.*}"
mkdir -p "$destination"/data/{pretrain,finetune}
mkdir -p "$destination"/{pretrain_ckpt,finetune_ckpt}
cp -r "$data_pre"/* "$destination/data/pretrain/"
cp -r "$data_fine"/* "$destination/data/finetune/"

# Run scripts || true, ensuring cleanup even on failure
# Pre-training, usually on multispecies wseg model
python "$code/$script1" \
    --initial_model_path "$model_in" \
    --train_dataset_folder "$destination/data/pretrain/" \
    --model_folder "$destination/pretrain_ckpt/" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size \
    || true

# Fine-tuning
python "$code/$script1" \
    --initial_model_path "$destination/pretrain_ckpt/final_checkpoint" \
    --train_dataset_folder "$destination/data/finetune" \
    --model_folder "$destination/finetune_ckpt/" \
    --gpu_list $gpus \
    --max_num_epochs $epochs \
    --batch_size $batch_size \
    || true

python "$code/$script2" \
    -d "$destination/data/finetune" \
    -m "$destination/finetune_ckpt/final_checkpoint_ct2" \
    -o "$output" \
    -i "$output_identifier" \
    || true

# Move finished model to target destination
mv "$destination/finetune_ckpt" "$model_out"

# Clean up: remove data, "<time>_<job>/" directory and parent directory, if empty
rm -rf "$destination"
if [ -z "$(ls -A "${destination%/*}")" ]; then
    rmdir "${destination%/*}"
fi
