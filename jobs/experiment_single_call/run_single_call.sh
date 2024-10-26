#!/bin/bash

for cfg in {1..7}
do
  echo "base moan+drop cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call/job_moan_drop.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "base moan+other cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_single_call/job_moan_other.sh "$cfg"
  done
done