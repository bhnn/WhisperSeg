#!/bin/bash

for cfg in {1..7}
do
  echo "base 9calls+drop cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_9call/job_9call_drop.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "base 9calls+other cfg: $cfg"
  for i in {1..5} # repetitions for robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_9call/job_9call_other.sh "$cfg"
  done
done