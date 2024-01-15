import argparse
from argparse import Namespace
from collections import defaultdict
from string import digits


def clean_tables(args: Namespace):
    with open(args.path, "r") as f:
        lines = [line.rstrip().split("\t") for line in f]
    d = defaultdict(lambda: 1)
    out = list()
    out.append(lines.pop(0)) # header
    for i in range(0, len(lines), 2):
        if not args.remove_fluff or lines[i][-1] != 'fluff':
            for j in [i, i+1]: # waveform part + spectrogram part
                lines[j][0] = str(d['id'])
                if lines[j][-1] not in ['p1', 'p2', 'p3']:
                    prefix = ''
                    if lines[j][-1][0] == '-':
                        prefix = '-'
                        stripped_label = lines[j][-1][1:].rstrip(digits)
                    else:
                        stripped_label = lines[j][-1].rstrip(digits)
                    lines[j][-1] = prefix + stripped_label + str(d[stripped_label])
                out.append(lines[j])
            d['id'] += 1
            d[stripped_label] += 1
    with open(args.path, "w") as f:
        f.write("\n".join(["\t".join(line) for line in out]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans up Raven selection tables: renumbers IDs, numbers labels, removes fluff")
    parser.add_argument("-p", "--path", type=str, help="Path to the .txt file", required=True)
    parser.add_argument("-f", "--fluff", action="store_true", help="Whether to remove fluff annotations (default: False)", dest="remove_fluff")
    args = parser.parse_args()

    clean_tables(args)