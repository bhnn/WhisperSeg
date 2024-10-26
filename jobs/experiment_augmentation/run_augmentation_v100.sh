#!/bin/bash

for cfg in {1..7}
do
  echo "large aug_unsupervised cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_augmentation/job_aug_unsupervised_v100.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "large aug_curated cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_augmentation/job_aug_curated_v100.sh "$cfg"
  done
done
