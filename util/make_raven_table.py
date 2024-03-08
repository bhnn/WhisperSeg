import argparse
import logging
from pathlib import Path
import json
import yaml
from os.path import join


def make_raven_tables(file_path: str, config_path: str, output_path: str = ""):
    with open(config_path, 'r') as f:
        classes = yaml.safe_load(f)
        classes.pop('misc', None) # to remove labels such as 'fluff' and 'help'
    for p in Path(file_path).rglob("*.jsonr"):
        logging.info(f"Found: {p}")
        with open(p, "r") as f:
            res_file = json.load(f)
        if len(res_file["onset"]) == len(res_file["offset"]) == len(res_file["cluster"]):
            id = 1
            out = ["Selection	View	Channel	Begin Time (s)	End Time (s)	Low Freq (Hz)	High Freq (Hz)	Delta Time (s)	Delta Freq (Hz)	Avg Power Density (dB FS/Hz)	Annotation"]
            for i in range(len(res_file["onset"])):
                out.append(f"{id}\tWaveform 1\t1\t{res_file['onset'][i]:.3f}\t{res_file['offset'][i]:.3f}\t0.000\t8000.000\t{res_file['offset'][i]-res_file['onset'][i]:.4f}\t8000.000\t\t{res_file['cluster'][i]}")
                out.append(f"{id}\tSpectrogram 1\t1\t{res_file['onset'][i]:.3f}\t{res_file['offset'][i]:.3f}\t0.000\t8000.000\t{res_file['offset'][i]-res_file['onset'][i]:.4f}\t8000.000\t\t{res_file['cluster'][i]}")
                id += 1
        out_path = join(p.absolute().parent, p.stem + "_PRED.Table.1.selections.txt")
        out_str = '\n'.join(o for o in out)
        with open(out_path, "w") as f:
            f.writelines(out_str)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    make_raven_tables("data/", "config/classes.yaml")