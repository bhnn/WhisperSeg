#!/bin/bash

for bs in 4 25 50
do
  for lr in 8e-5 3e-6 8e-6
  do
    for cfg in {1..7}
    do
      echo "batch size: $bs, learning_rate: $lr, cfg: $cfg"
      for i in {1..5} # repetitions fo robust average
      do
        sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_bslr/job_bslr.sh "$bs" "$lr" "$cfg"
      done
    done
  done
done
