#!/bin/bash

for cfg in {1..7}
do
  echo "cfg: $cfg"
  for i in {1..5} # repetitions fo robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_pre_parent/job_pre_parent.sh "$cfg"
  done
done