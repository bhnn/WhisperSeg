#!/bin/bash

for cfg in {1..7}
do
  echo "large moan+vocal cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call/job_1call_vocal_v100.sh "$cfg"
  done
done