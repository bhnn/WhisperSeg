#!/bin/bash

for cfg in {1..7}
do
  echo "base 1calls+drop cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call_balanced/job_single_call_balanced_drop.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "base 1calls+other cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call_balanced/job_single_call_balanced_other.sh "$cfg"
  done
done