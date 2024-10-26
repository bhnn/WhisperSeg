import argparse
from collections import defaultdict
from string import digits

from common import get_flex_file_iterator


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
    # create list of waveform + spectrogram pairs
    lines = [[lines[i], lines[i+1]] for i in range(0, len(lines), 2)]
    # sort list by begin time of waveform part (WhisperSeg .json files need to be sorted by begin times of entries)
    lines = sorted(lines, key=lambda x: float(x[0][3]))
    for l in lines:
        if not remove_fluff or (not l[0][-1].startswith('fluff')):
            for part in l: # waveform part + spectrogram part
                # renumber IDs
                part[0] = str(d['id'])
                # leave p1/2/3 as labels
                if part[-1] not in ['p1', 'p2', 'p3']:
                    # handling experimental prefixing of annotations for focal/non-focal calls
                    idx = 1 if part[-1][0] == '-' else 0
                    prefix = '-' if part[-1][0] == '-' else ''
                    label = part[-1][idx:].rstrip(digits)
                    part[-1] = str(prefix) + str(label) + str(d[label])
            out.append(l)
            d['id'] += 1
            d[label] += 1
    out = [out.pop(0)] + [item for sublist in out for item in sublist]
    with open(path, "w") as f:
        f.write("\n".join(["\t".join(line) for line in out]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans up Raven selection tables: renumbers IDs, numbers labels, removes fluff")
    parser.add_argument("-p", "--path", type=str, help="Path to the selection table.txt file", required=True)
    parser.add_argument("-f", "--fluff", action="store_true", help="Whether to remove 'fluff' annotations (default: False)", dest="remove_fluff")
    args = parser.parse_args()

    c = 0
    for p in get_flex_file_iterator(args.path, rglob_str="*.txt"):
        clean_tables(path=p)
        c += 1
    print(f"Cleaned up {c} files.")