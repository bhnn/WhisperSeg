import argparse
import re
from itertools import chain

from common import get_flex_file_iterator


def find(target, iterable):
    for i in range(len(iterable)):
        if iterable[i] == target:
            return i

def parse_slurm_files(log_path: str, from_id: int, to_id: int) -> None:
    """Parses SLURM log files for classification_report() outputs. Includes the jobs with IDs from `from_id` to `to_id`.
       Does not work for slurm files that contain more than one target type (e.g. only moan or target).

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
            with open(log, 'r') as f:
                res = [r for r in [re.findall(r'^\s+\w+\s+((?:\d+\.\d+|nan))\s+((?:\d+\.\d+|nan))\s+((?:\d+\.\d+|nan))\s.*$', line, re.MULTILINE) for line in f] if r]
            if len(res) != 2:
                raise ValueError(f'Expected to find 6 values total (file {log.name})')
            stats.append([(x if x != 'nan' else '0.00') for x in [log_id, *chain.from_iterable(res[0]), *chain.from_iterable(res[1])]])
            
    print("<job_id> <mo_precision> <mo_recall> <mo_f1> <vocal_precision> <vocal_recall> <vocal_f1>")
    for stat in sorted(stats):
        print("{} {:.4} {:.4} {:.4} {:.4} {:.4} {:.4}".format(*stat))
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses SLURM log files for classification_report() outputs.")
    parser.add_argument("-p", "--log_path", type=str, help="Directory containing slurm job files", default="/usr/users/bhenne/projects/whisperseg/slurm_files")
    parser.add_argument("-a", "--from_id", type=int, help="Job ID of first run to search for", required=True)
    parser.add_argument("-z", "--to_id", type=int, help="Job ID of last run to search for", required=True)
    args = parser.parse_args()

    parse_slurm_files(**vars(args))
