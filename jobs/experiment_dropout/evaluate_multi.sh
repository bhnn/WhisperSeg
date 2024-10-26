#!/bin/bash

cfg_count=5
for job_id in {537461..537495}
do
  file_name=$(find /usr/users/bhenne/projects/whisperseg/model/ -type d -name "*j$job_id*")
  sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call/evaluate_1call.sh $file_name $((cfg_count / 5))
  ((cfg_count++))
done
