#!/bin/bash

for vratio in 0.1 0.2
do
  for cfg in {1..7}
  do
    echo "vratio: $vratio, cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_vratio/job_vratio.sh "$vratio" "$cfg"
    done
  done
done

