#!/bin/bash

for clipd in "25" "50" "75" "300"
do
  for cfg in {1..7}
  do
    echo "clipd: $clipd, cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_clipd/job_clipd.sh "$clipd" "$cfg"
    done
  done
done

