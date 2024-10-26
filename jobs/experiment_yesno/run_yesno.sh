#!/bin/bash

for pat in 10 20
do
  for cfg in {1..7}
  do
    echo "patience: $pat, cfg: $cfg"
    for i in {1..5} # repetitions fo robust average
    do
      sbatch /usr/users/bhenne/projects/whisperseg/jobs/experiment_yesno/job_yesno.sh "$pat" "$cfg"
    done
  done
done