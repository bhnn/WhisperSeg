#!/bin/bash

for i in {1..7}
do
  echo "Data config: $i"
  
  for j in {1..5}
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_baseline/job_baseline.sh "$j"
  done
done
