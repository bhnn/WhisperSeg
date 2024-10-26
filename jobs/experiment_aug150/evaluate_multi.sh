#!/bin/bash

cfg_count=4
for job_id in {1167049..1167051}
do
  file_name=$(find /usr/users/bhenne/projects/whisperseg/model/ -type d -name "*$job_id*")
  sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_aug150/evaluate_aug150.sh $file_name $cfg_count
done
