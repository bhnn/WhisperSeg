import argparse
from argparse import Namespace
from collections import defaultdict
from string import digits


def clean_tables(path: str, remove_fluff: bool = False):
    """Cleans up Raven selection tables: renumbers IDs, numbers labels

    Args:
        path (str): Path to the selection table .txt file
        remove_fluff (bool, optional): Whether to remove fluff annotations. Defaults to False.
    """
    with open(path, "r") as f:
        lines = [line.rstrip().split("\t") for line in f]
    d = defaultdict(lambda: 1)
    out = list()
    out.append(lines.pop(0)) # header
    for i in range(0, len(lines), 2):
        if not remove_fluff or lines[i][-1] != 'fluff':
            for j in [i, i+1]: # waveform part + spectrogram part
                # renumber IDs, Raven can produce gaps in the numbering
                lines[j][0] = str(d['id'])
                # leave p1/2/3 as labels
                if lines[j][-1] not in ['p1', 'p2', 'p3']:
                    # handling experimental prefixing of annotations for focal/non-focal calls
                    prefix = 1 if lines[i][-1][0] == '-' else 0
                    label = lines[i][-1][prefix:].rstrip(digits)
                    lines[j][-1] = prefix + label + str(d[label])
                out.append(lines[j])
            d['id'] += 1
            d[label] += 1
    with open(args.path, "w") as f:
        f.write("\n".join(["\t".join(line) for line in out]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans up Raven selection tables: renumbers IDs, numbers labels, removes fluff")
    parser.add_argument("-p", "--path", type=str, help="Path to the selection table.txt file", required=True)
    parser.add_argument("-f", "--fluff", action="store_true", help="Whether to remove fluff annotations (default: False)", dest="remove_fluff")
    args = parser.parse_args()

    clean_tables(**vars(args))