import argparse
import logging
from collections import defaultdict
from pathlib import Path
from string import digits
from typing import List

classes = {
        'P1': ['p1', 'b', 'ca', 'c', 'cl', 'cm', 'e', 'ht', 'l', 'm', 'n', 'o', 'pc', 'sh', 'ud'],
        'P2': ['p2', 'd', 'hw', 'h', 'mo', 'pu', 'up', 'w'], 
        'P3': ['p3', 'ho', 'hu', 'se', 'sk', 'sq', 't', 'wa', 'y'],
        'misc': ['fluff', 'help'],
    }

def count(path: str) -> List[defaultdict]:
    """Counts the number of annotations per label in all .txt files in a directory recursively

    Args:
        path (str): Path to the directory containing the .txt files

    Returns:
        List[defaultdict]: List of dictionaries containing the number of annotations per label
    """
    dicts = []
    for p in Path(path).rglob("*.txt"):
        logging.info(f"Found: {p}")
        with open(p, "r") as f:
            # split standard raven selection table format into list of lists and drop the header
            lines = [line.rstrip().split("\t") for line in f][1:]
        d = defaultdict(int)
        # iterate over selection table list in steps of 2 (waveform part + spectrogram part)
        for i in range(0, len(lines), 2):
            prefix = 1 if lines[i][-1][0] == '-' else 0
            # count parent classe separately
            if lines[i][-1][prefix:] not in ['p1', 'p2', 'p3']:
                label = lines[i][-1][prefix:].rstrip(digits)
            else:
                label = lines[i][-1][prefix:]
            d[label] += 1
        dicts.append(d)
    print(f"Processed {len(dicts)} files.")
    return dicts

def sum_dicts(dicts: list) -> defaultdict:
    """Sums up the number of annotations per label in a list of dictionaries.

    Args:
        dicts (list): List of dictionaries containing the number of annotations per label

    Returns:
        defaultdict: Dictionary containing the sum of all annotations per label
    """
    d = defaultdict(int)
    total1 = total2 = 0
    not_counted = []
    for di in dicts:
        for k, v in di.items():
            if any(k in sublist for sublist in classes.values()):
                d[k] += v
                total1 += v
            else:
                not_counted.append(k)
            total2 += v
    if total1 != total2:
        logging.warning(f"Total annotations: {total2}, but sum of annotations per label: {total1}")
    if len(not_counted) > 0:
        logging.warning(f"Labels not counted: {set(not_counted)}")
    return d, total1

def pretty_print(d: defaultdict, show_zeros: bool = True):
    """Pretty prints the number of annotations per label

    Args:
        d (defaultdict): Dictionary containing the sums of all annotations per label
        show_zeros (bool, optional): Whether to show annotations with 0 occurrences. Defaults to True.
    """
    if show_zeros:
        stats = '\n'.join((cl + ':    ' + f'{"":>4}'.join([f"{k:>2}: {d[k]:>2}" for k in classes[cl]])) for cl in classes.keys())
    else:
        stats = '\n'.join((cl + ':    ' + f'{"":>4}'.join([f"{k:>2}: {d[k]:>2}" for k in classes[cl] if d[k] > 0])) for cl in classes.keys())
    print(stats)

def annotation_statistics(args: argparse.Namespace):
    """Assembles statistics for Raven selection tables in directory recursively: number of annotations per label

    Args:
        args (argparse.Namespace): Command line arguments containing at least a file path as `path`
    """
    d, total = sum_dicts(count(args.path))
    pretty_print(d)
    print(f"Total annotations: {total}")

if __name__ == "__main__":
    logging.basicConfig(
        # filename='annotation_statistics.log',
        # filemode='a',
        # level=logging.INFO,
    )
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Assembles statistics for Raven selection tables in directory recursively: number of annotations per label")
    parser.add_argument("-p", "--path", type=str, help="Path to the .txt file", required=True)
    args = parser.parse_args()

    annotation_statistics(args)