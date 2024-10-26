#!/bin/bash

for tolerance in "075" "1" "2"
do
  for cfg in {1..7}
  do
    echo "tolerance: $tolerance, cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_tolerance/job_tolerance_2.sh "$tolerance" "$cfg"
    done
  done
done

