import argparse
import json
import logging
from os.path import join
from pathlib import Path

import yaml


def make_raven_tables(file_path: str, extension: str, config_path: str, output_path: str = ""):
    """Converts WhisperSeg inference results into Raven selection tables

    Args:
        file_path (str): Path to .jsonr inference files.
        extension (str): Extention of the inference files: either jsonr or json, defaults to jsonr
        config_path (str): Path to the config file detailing all annotation classes.
        output_path (str, optional): Path to an output directory. Defaults to the input directory.
    """
    with open(config_path, 'r') as f:
        classes = yaml.safe_load(f)
        classes.pop('misc', None) # to remove labels such as 'fluff' and 'help'
    for p in Path(file_path).rglob(f"*.{extension}"):
        logging.info(f"Found: {p}")
        with open(p, "r") as f:
            res_file = json.load(f)
        if len(res_file["onset"]) < 1:
            continue
        if len(res_file["onset"]) == len(res_file["offset"]) == len(res_file["cluster"]):
            id = 1
            out = ["Selection	View	Channel	Begin Time (s)	End Time (s)	Low Freq (Hz)	High Freq (Hz)	Delta Time (s)	Delta Freq (Hz)	Avg Power Density (dB FS/Hz)	Annotation"]
            for i in range(len(res_file["onset"])):
                out.append(f"{id}\tWaveform 1\t1\t{res_file['onset'][i]:.3f}\t{res_file['offset'][i]:.3f}\t0.000\t8000.000\t{res_file['offset'][i]-res_file['onset'][i]:.4f}\t8000.000\t\t{res_file['cluster'][i]}")
                out.append(f"{id}\tSpectrogram 1\t1\t{res_file['onset'][i]:.3f}\t{res_file['offset'][i]:.3f}\t0.000\t8000.000\t{res_file['offset'][i]-res_file['onset'][i]:.4f}\t8000.000\t\t{res_file['cluster'][i]}")
                id += 1
        out_str = '\n'.join(o for o in out)
        if output_path == None:
            new_path = p.parent.absolute()
        else:
            new_path = output_path
        out_path = join(new_path, p.stem + "_PRED.Table.1.selections.txt")
        with open(out_path, "w") as f:
            f.writelines(out_str)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Converts WhisperSeg inference results into Raven selection tables")
    parser.add_argument("-p", "--file_path", type=str, help="Path to inference files", required=True)
    parser.add_argument("-e", "--extension", type=str, help="Extention of the inference files: either jsonr or json", default="jsonr")
    parser.add_argument("-c", "--config_path", type=str, help="Path to the config file detailing all annotation classes", default='./config/classes.yaml')
    parser.add_argument("-o", "--output_path", type=str, help="Path to the output .txt  selection table files. Defaults to the input directory.", default=None)
    args = parser.parse_args()

    make_raven_tables(**vars(args))