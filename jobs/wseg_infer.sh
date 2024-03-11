#!/bin/bash

#SBATCH --gres=gpu:rtx5000:4
#SBATCH -p gpu
#SBATCH -t 2-00:00:00
#SBATCH -o /usr/users/bhenne/projects/whisperseg/slurm_files/job-%J.out

cd /local/eckerlab/

if [ ! -d "Individual" ]
then
    tar xf /usr/users/vogg/Labelling/Lemurs/Individual_imgs.tar
fi

source activate wseg

# -d data/lemur_snippet_1/train/
dataset_path="/local/eckerlab/wseg_data"
model_path="/usr/users/bhenne/projects/whisperseg/model/whisperseg-lemur-finetuned-snip1/final_checkpoint_ct2"
output_dir="/usr/users/bhenne/projects/whisperseg/results"

python infer.py --data_dir "$dataset_path" --model_path "$model_path" --output_dir "$output_dir" 

rm -rf /local/eckerlab/wseg_data


#Amb,Cam,Cha,Che,Flo,Gen,Geo,Har,Her,Isa,Kai,Lat,Mya,Pal,Rab,Red,Sap,Taj