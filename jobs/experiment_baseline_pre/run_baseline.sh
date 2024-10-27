#!/bin/bash

for cfg in {1..7}
do
  echo "base, cfg: $cfg"
  
  for j in {1..5}
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_baseline/job_baseline.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "large, cfg: $cfg"
  
  for j in {1..5}
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_baseline/job_baseline_v100.sh "$cfg"
  done
done