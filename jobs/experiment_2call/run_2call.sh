#!/bin/bash

for cfg in {1..7}
do
  echo "base 2call cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_2call/job_2call.sh "$cfg"
  done
done
