import argparse
import json
from pathlib import Path
from typing import List

from common import get_flex_file_iterator


def summarise_res(file: Path) -> List:
    """Summarises evaluation results from a file.

    Args:
        file (Path): Path to the evaluation result file

    Returns:
        (List): List of summarised results
    """
    with open(file, 'r') as f:
        data = json.load(f)
    return [
        job_id,
        data['segment_wise_scores']['precision'],
        data['segment_wise_scores']['recall'],
        data['segment_wise_scores']['F1'],
        data['frame_wise_scores']['precision'],
        data['frame_wise_scores']['recall'],
        data['frame_wise_scores']['F1'],
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarises result .txt files in specified directory that fall between `from` and `to` job IDs.")
    parser.add_argument("-p", "--path", required=True, help="Path to directory containing result files from evaluate.py")
    parser.add_argument("-a", "--from_id", required=True, help="Job ID to start with, inclusive")
    parser.add_argument("-z", "--to_id", required=True, help="Job ID to end with, inclusive")
    args = parser.parse_args()

    print("<job_id> <segment_precision> <segment_recall> <segment_f1> <framewise_precision> <framewise_recall> <framewise_f1>")
    out = []
    for file in get_flex_file_iterator(args.path, '*.txt'):
        # eval filename syntax: <date>_<time>_eval_<base/large>_j<job_id>.txt
        job_id = file.name.split('j')[1][:-4]
        if args.from_id <= job_id <= args.to_id:
            out.append(summarise_res(file=file))
        else:
            continue

    out = sorted(out)
    for line in out:
        print("{} {:.4} {:.4} {:.4} {:.4} {:.4} {:.4}".format(*line))
