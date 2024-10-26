#!/bin/bash

for dropout in 0.1 0.3 0.5
do
  for cfg in {1..7}
  do
    echo "dropout: $dropout cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_dropout/job_dropout.sh "$dropout" "$cfg"
    done
  done
done