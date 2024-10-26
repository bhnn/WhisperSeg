import argparse
import logging
from collections import defaultdict
from pathlib import Path
from string import digits
from typing import List

import yaml
from common import get_flex_file_iterator


def count(path: str) -> List[defaultdict]:
    """Counts the number of annotations per label in all .txt files in a directory recursively, or in a single file if specified.

    Args:
        path (str): Path to the directory containing the .txt files

    Returns:
        List[defaultdict]: List of dictionaries containing the number of annotations per label
    """
    dicts = []
    for p in get_flex_file_iterator(path):
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

def sum_dicts(dicts: list, classes: dict) -> defaultdict:
    """Sums up the number of annotations per label in a list of dictionaries.

    Args:
        dicts (list): List of dictionaries containing the number of annotations per label
        classes (dict): Dictionary containing the valid annotation labels

    Returns:
        defaultdict: Dictionary containing the sum of all annotations per label
        total1 (int): Total number of annotations
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

def pretty_print(d: defaultdict, classes: dict, show_zeros: bool = True):
    """Pretty prints the number of annotations per label

    Args:
        d (defaultdict): Dictionary containing the sums of all annotations per label
        classes (dict): Dictionary containing the valid annotation labels
        show_zeros (bool, optional): Whether to show annotations with 0 occurrences. Defaults to True.
    """
    if show_zeros:
        stats = '\n'.join((cl + ':  ' + f'{"":>4}'.join([f"{k:>2}: {d[k]:>3}" for k in classes[cl]])) for cl in classes.keys())
    else:
        stats = '\n'.join((cl + ':  ' + f'{"":>4}'.join([f"{k:>2}: {d[k]:>3}" for k in classes[cl] if d[k] > 0])) for cl in classes.keys())
    print(stats)

def annotation_statistics(path: str, config_path: str, mode: str):
    """Assembles statistics for Raven selection tables in directory recursively: number of annotations per label

    Args:
        path (str): Path to directory in which to search for selection table .txt files
        config_path (str): Path to the config file detailing all annotation classes
    """
    with open(config_path, 'r') as f:
        classes = yaml.safe_load(f)
    d, total = sum_dicts(count(path), classes)
    if mode == "moan_vocal":
        print(f"Moan samples: {d['mo']}")
        print(f"Vocal samples: {total - d['mo']}")
    elif mode == "all":
        pretty_print(d, classes)
        print(f"Total annotations: {total}")
    elif mode == "thesis":
        # [ cl,   m,   l,  ca, sh,  b, pc, p1, cm,       +           h,  pu,  mo,  w, p2, +        t, sq,  y, hu, + ],
        # cut: P1: ht, o, ud, n, e, c; P2: hw, d, up; P3: p3, se, sk, wa, ho
        print(f"{d['cl']}, {d['m']}, {d['l']}, {d['ca']}, {d['sh']}, {d['b']}, {d['pc']}, {d['p1']}, {d['cm']}, {d['ht']+d['o']+d['ud']+d['n']+d['e']+d['c']}, {d['h']}, {d['pu']}, {d['mo']}, {d['w']}, {d['p2']}, {d['hw']+d['d']+d['up']}, {d['t']}, {d['sq']}, {d['y']}, {d['hu']}, {d['p3']+d['se']+d['sk']+d['wa']+d['ho']}")
        print('Total annotatios: ', d['cl'] + d['m'] + d['l'] + d['ca'] + d['sh'] + d['b'] + d['pc'] + d['p1'] + d['cm'] + d['ht']+d['o']+d['ud']+d['n']+d['e']+d['c'] + d['h'] + d['pu'] + d['mo'] + d['w'] + d['p2'] + d['hw']+d['d']+d['up'] + d['t'] + d['sq'] + d['y'] + d['hu'] + d['p3']+d['se']+d['sk']+d['wa']+d['ho'])
    else:
        logging.warning(f"Unknown mode: {mode}")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Assembles statistics for Raven selection tables in directory recursively: number of annotations per label")
    parser.add_argument("-p", "--path", type=str, help="Path to directory in which to search for selection table .txt files", required=True)
    parser.add_argument("-s", "--show_per_file", action="store_true", help="Show the number of annotations per label per file")
    parser.add_argument("-c", "--config-path", type=str, help="Path to the config file detailing all annotation classes", default='./config/classes.yaml')
    parser.add_argument("-m", "--mode", choices=['all', 'moan_vocal', 'thesis'], nargs="?", const="all", default="all", help="Whether to show all annotations, only moan and vocal annotations, or a thesis-friendly format. Defaults to %(default)s.")
    args = parser.parse_args()

    if args.show_per_file:
        for p in get_flex_file_iterator(args.path):
            print(f'- File {p} contains:')
            annotation_statistics(p, args.config_path, args.mode)
            print()
    else:
        annotation_statistics(args.path, args.config_path, args.mode)