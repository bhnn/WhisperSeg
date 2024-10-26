#!/bin/bash

for cfg in {1..7}
do
  echo "base cfg: $cfg"
  for i in {1..5} # repetitions fo robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_baseline2/job_baseline2.sh "$cfg"
  done
done

for cfg in {1..7}
do
  echo "large cfg: $cfg"
  for i in {1..5} # repetitions fo robust average
  do
    sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_baseline2/job_baseline2_v100.sh "$cfg"
  done
done