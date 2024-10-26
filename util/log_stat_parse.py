import argparse
import re

import numpy as np
from common import get_flex_file_iterator


def parse_slurm_files(log_path: str, from_id: int, to_id: int) -> None:
    """Parses SLURM log files for classification_report() outputs. Includes the jobs with IDs from `from_id` to `to_id`.
       Can find different targets _per file_, that doesn't make much sense in a table though. BUT it can handle files that
       have been balanced using utils/balance_cuts.py.

    Args:
        log_path (str): Path to the directory containing the SLURM log files.
        from_id (int): ID of the first job to include in the summary.
        to_id (int): ID of the last job to include in the summary.

    Raises:
        ValueError: If the number of values found in a log file is not 6.
    """
    stats = []
    for log in get_flex_file_iterator(file_path=log_path, rglob_str='*.out'):
        # (my) convention for log names: 'job-<numerical_id>.out'
        log_id = int(log.name[4:-4])
        if from_id <= log_id <= to_id:
            file_targets = []
            target = [[], [], []] # collect targets/vocals per file (can be more than 1 when using balancing)
            vocal = [[], [], []]
            with open(log, 'r') as f:
                res = [r for r in [re.findall(r'^\s+(\w+)\s+((?:\d+\.\d+|nan))\s+((?:\d+\.\d+|nan))\s+((?:\d+\.\d+|nan))\s.*$', line, re.MULTILINE) for line in f] if r]
            for r in res: # matches one-by-one
                (t, *val) = r[0] # [('..'), ('..') ...]
                if t in ['mo', 'target']:
                    file_targets.append(t)
                    for i,v in enumerate(val):
                        target[i].append(float(v) if v != 'nan' else 0.00)
                elif t in ['vocal']:
                    for i,v in enumerate(val):
                        vocal[i].append(float(v) if v != 'nan' else 0.00)
                else:
                    raise ValueError(f'Unknown target encountered (file {log.name})')
            if len(set(file_targets)) > 1:
                raise ValueError(f'Mixed targets found, can only process 1 type of targets (file {log.name})')
            stats.append([log_id] + [np.mean(v) if v else 0.00 for v in (target+vocal)])
            
    print("<job_id> <t_precision> <t_recall> <t_f1> <vocal_precision> <vocal_recall> <vocal_f1>")
    for stat in sorted(stats):
        print("{} {:.4} {:.4} {:.4} {:.4} {:.4} {:.4}".format(*stat))
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses SLURM log files for classification_report() outputs.")
    parser.add_argument("-p", "--log_path", type=str, help="Directory containing slurm job files", default="/usr/users/bhenne/projects/whisperseg/slurm_files")
    parser.add_argument("-a", "--from_id", type=int, help="Job ID of first run to search for", required=True)
    parser.add_argument("-z", "--to_id", type=int, help="Job ID of last run to search for", required=True)
    args = parser.parse_args()

    parse_slurm_files(**vars(args))
