import argparse
import json
import logging
from os.path import join
from pathlib import Path
from string import digits

import yaml


def make_json(file_path: str, config_path: str, species: str, sampling_rate: int, min_frequency: int, spec_time_step: 
              float, tolerance: float, time_per_frame: float, epsilon: float, output_path: str = ""):
    """Converts Raven selection tables to .json files for WhisperSeg use

    Args:
        file_path (str): Path in which to recursively look for .txt files of selection tables
        config_path (str): Path to the config file detailing all annotation classes
        species (str): Species string to prepend to the labels
        sampling_rate (int): Sampling rate of the audio
        min_frequency (int): Minimum frequency for computing the Log Melspectrogram. Components below min_frequency will not be included in the input spectrogram.
        spec_time_step (float): Spectrogram Time Resolution. By default, one single input spectrogram of WhisperSeg contains 1000 columns.
        min_segment_length (float): The minimum allowed length of predicted segments. The predicted segments whose length is below 'min_segment_length' will be discarded. Defaults to 0, then automatically determ shortest segment from annotations
        tolerance (float): When computing the F1_seg score, we need to check if both the absolute difference between the predicted onset and the ground-truth onset and the absolute difference between the predicted and ground-truth offsets are below a tolerance (in second)
        time_per_frame (float): The time bin size (in second) used when computing the F1_frame score.
        epsilon (float): The threshold epsilon_vote during the multi-trial majority voting when processing long audio files
        output_path (str): Path to the output .json file. Defaults to the input directory.
    """
    files = 0
    completed_files = dict()
    smallest_segment = float('inf')
    with open(config_path, 'r') as f:
        classes = yaml.safe_load(f)
        classes.pop('misc', None) # to remove labels such as 'fluff' and 'help'
    for p in Path(file_path).rglob("*.txt"):
        logging.info(f"Found: {p}")
        with open(p, "r") as f:
            # split standard raven selection table format into list of lists and drop the header
            lines = [line.rstrip().split("\t") for line in f][1:]
        content = {
            "onset": [],
            "offset": [],
            "cluster": [],
            "species": species,
            "sr": sampling_rate,
            "min_frequency": min_frequency,
            "spec_time_step": spec_time_step,
            "min_segment_length": float(min([l[7] for l in lines])), # Delta Time (s) column in Raven tables
            "tolerance": tolerance,
            "time_per_frame_for_scoring": time_per_frame,
            "eps": epsilon,
        }
        smallest_segment = min(smallest_segment, content["min_segment_length"])
        logging.info(f"smallest_segment so far: {smallest_segment:>7.5f}")
        # iterate over selection table list in steps of 2 (waveform part + spectrogram part)
        invalid = []
        for i in range(0, len(lines), 2):
            prefix = 1 if lines[i][-1][0] == '-' else 0
            # count parent classe separately
            if lines[i][-1][prefix:] not in ['p1', 'p2', 'p3']:
                label = lines[i][-1][prefix:].rstrip(digits)
            else:
                label = lines[i][-1][prefix:]
            if any(label in sublist for sublist in classes.values()):
                content["onset"].append(float(lines[i][3]))
                content["offset"].append(float(lines[i][4]))
                content["cluster"].append(label)
            else:
                invalid.append(label)
        if len(invalid) > 0:
            logging.warning(f"Invalid labels found in {p}: {set(invalid)}. These have been ignored in the output file.")
        if output_path == "":
            new_path = p.parent.absolute()
        else:
            new_path = output_path
        # removes "".Table.1.selections.txt" from the end of the file name
        new_path = join(new_path, p.stem.split('.')[0] + '.json')
        completed_files[new_path] = content
        files += 1

    for file_name, content in completed_files.items():
        # unify min_segment_length across all files
        content["min_segment_length"] = smallest_segment
        with open(file_name, "w") as fp:
            json.dump(content, fp, indent=2)
    print(f"Processed {files} files.")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Prepares Raven selection tables for WhisperSeg use: convert to .json and add some more info")
    parser.add_argument("-p", "--file_path", type=str, help="Path to .txt selection table files", required=True)
    parser.add_argument("-c", "--config_path", type=str, help="Path to the config file detailing all annotation classes", default='./config/classes.yaml')
    parser.add_argument("-s", "--species", type=str, help="The species in the audio, e.g., \"zebra_finch\" When adding new species, go to the WhisperSeg load_model() function in model.py, add a new pair of species_name:species_token to the species_codebook variable. E.g., \"catta_lemur\":\"<|catta_lemur|>\".", default='catta_lemur')
    parser.add_argument("-r", "--sampling_rate", type=int, help="The sampling rate that is used to load the audio. The audio file will be resampled to the sampling rate specified by this, regardless of the native sampling rate of the audio file.", default=48000)
    parser.add_argument("-f", "--min_frequency", type=int, help="The minimum frequency when computing the Log Melspectrogram. Frequency components below min_frequency will not be included in the input spectrogram.", default=0)
    parser.add_argument("-t", "--spec_time_step", type=float, help="Spectrogram Time Resolution. By default, one single input spectrogram of WhisperSeg contains 1000 columns. 'spec_time_step' represents the time difference between two adjacent columns in the spectrogram. It is equal to FFT_hop_size / sampling_rate", default=0.0025)
    parser.add_argument("-d", "--tolerance", type=float, help="When computing the F1_seg score, we need to check if both the absolute difference between the predicted onset and the ground-truth onset and the absolute difference between the predicted and ground-truth offsets are below a tolerance (in second)", default=0.01)
    parser.add_argument("-i", "--time_per_frame", type=float, help="The time bin size (in second) used when computing the F1_frame score.", default=0.001)
    parser.add_argument("-e", "--epsilon", type=float, help="The threshold epsilon_vote during the multi-trial majority voting when processing long audio files", default=0.02)
    parser.add_argument("-o", "--output_path", type=str, help="Path to the output .json file. Defaults to the input directory.", default="")
    args = parser.parse_args()

    make_json(**vars(args))