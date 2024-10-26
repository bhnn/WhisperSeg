#!/bin/bash

cfg_count=5
for job_id in {692207..692241}
do
  file_name=$(find /usr/users/bhenne/projects/whisperseg/model/ -type d -name "*$job_id*")
  sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_9call/evaluate_9call.sh $file_name $((cfg_count / 5))
  ((cfg_count++))
done
