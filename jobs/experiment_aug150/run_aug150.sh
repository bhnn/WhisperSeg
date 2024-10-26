#!/bin/bash

for cfg in {1..7}
do
  echo "base aug_150 unsupervised cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_aug150/job_aug150.sh "$cfg"
  done
done
