#!/bin/bash

for cfg in {1..10}
do
  echo "base aug_curated cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_augmentation/job_aug_curated.sh "$cfg"
  done
done