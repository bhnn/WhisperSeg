#!/bin/bash

for pat in 3 10 25
do
  for cfg in {1..7}
  do
    echo "patience: $pat, cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_patience/job_patience.sh "$pat" "$cfg"
    done
  done
done
