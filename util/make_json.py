import argparse
import json
import logging
from os.path import join
from string import digits
from sys import exit
from typing import List

import yaml
from common import (compute_annotation_metadata, compute_spec_time_step,
                    get_flex_file_iterator)
from scipy.io import wavfile


def fetch_sr_rounded(wav_path: str) -> int:
    """Fetches the sampling rate from a wav file and rounds it to the nearest 10s value (22050 -> 22000).

    Args:
        wav_path (str): Path to the wav file

    Returns:
        int: The rounded sampling rate
    """
    return round(
        wavfile.read(wav_path)[0], # [sampling_rate, data]
        -2)

def make_json(file_path: str, config_path: str, convert_annotations: str, filter: List, merge_targets: bool, species: str, clip_duration: float, min_frequency: int,
    tolerance: float, time_per_frame: float, epsilon: float, output_path: str = ""):
    """Converts Raven selection tables to .json files for WhisperSeg use

    Args:
        file_path (str): Path in which to recursively look for .txt files of selection tables
        config_path (str): Path to the config file detailing all annotation classes
        convert_annotations (str): Whether to abstract annotations into their parent classes or leave them unchanged. 'None' uses all annotations as provided, 'parent' converts all child annotations into their parent class, 'animal' converts all annotations to "vocal".
        filter (List): List of allowed labels, or none to process all labels.
        species (str): Species string to prepend to the labels
        clip_duration (float): Length D of the audio clips each file will be divided into by the algorithm. Used here to compute hop length L and spec_time_step.
        min_frequency (int): Minimum frequency for computing the Log Melspectrogram. Components below min_frequency will not be included in the input spectrogram.
        tolerance (float): When computing the F1_seg score, we need to check if both the absolute difference between the predicted onset and the ground-truth onset and the absolute difference between the predicted and ground-truth offsets are below a tolerance (in second)
        time_per_frame (float): The time bin size (in second) used when computing the F1_frame score.
        epsilon (float): The threshold epsilon_vote during the multi-trial majority voting when processing long audio files
        output_path (str): Path to the output .json file. Defaults to the input directory.
    """
    files = 0
    completed_files = dict()
    with open(config_path, 'r') as f:
        classes = yaml.safe_load(f)
        classes.pop('misc', None) # to remove labels such as 'fluff' and 'help'
    if not filter and convert_annotations in ["parent_filter_replace", "animal_filter_replace", "parent_filter_drop", "animal_filter_drop"]:
        print(f"make_json.py: argument -a/--convert_annotations: \"{convert_annotations}\" requires a valid list of filters.")
        exit(1)
    if convert_annotations == "none":
        # no conversion, just use the labels as they are
        if filter:
            transition_matrix = {vv: vv for v in classes.values() for vv in v if vv in filter}
        else:
            transition_matrix = {vv: vv for v in classes.values() for vv in v}
    elif convert_annotations == "parent":
        # replace all self-lookups with parent class, "inverse lookup" basically
        transition_matrix = {vv: k.lower() for k, v in classes.items() for vv in v}
    elif convert_annotations == "parent_filter_replace":
        # replace all labels that do not match a filter with parent class, keep filter matches as they are
        transition_matrix = {vv: (k.lower() if vv not in filter else vv) for k, v in classes.items() for vv in v}
    elif convert_annotations == "parent_filter_drop":
        # replace all labels that match a filter with parent class, drop everything else
        transition_matrix = {vv: k.lower() for k, v in classes.items() for vv in v if vv in filter}
    elif convert_annotations == "animal":
        # replace all self-lookups with "vocal"
        transition_matrix = {vv: "vocal" for v in classes.values() for vv in v}
    elif convert_annotations == "animal_filter_replace":
        # replace all labels that do not match a filter with "vocal", keep filter matches as they are
        transition_matrix = {vv: ("vocal" if vv not in filter else vv) for v in classes.values() for vv in v}
    elif convert_annotations == "animal_filter_drop":
        # replace all labels that match a filter with "vocal", drop everything else
        transition_matrix = {vv: "vocal" for v in classes.values() for vv in v if vv in filter}
    for p in get_flex_file_iterator(file_path, rglob_str="*.txt"):
        logging.info(f"Found: {p}")
        with open(p, "r") as f:
            # split standard raven selection table format into list of lists and drop the header
            lines = [line.rstrip().split("\t") for line in f][1:]
        split_stem = p.stem.split('.')[0]
        sampling_rate = fetch_sr_rounded(join(p.parent.absolute(), split_stem + '.wav'))
        hop_length = compute_annotation_metadata(duration=clip_duration, sampling_rate=sampling_rate)
        spec_time_step = compute_spec_time_step(sampling_rate, hop_length)
        content = {
            "onset": [],
            "offset": [],
            "cluster": [],
            "species": species if convert_annotations != "animal" else "animal",
            "sr": sampling_rate,
            "min_frequency": min_frequency,
            "spec_time_step": spec_time_step,
            "min_segment_length": float(min([l[7] for l in lines])), # Delta Time (s) column in Raven tables
            "tolerance": tolerance,
            "time_per_frame_for_scoring": time_per_frame,
            "eps": epsilon,
        }
        # iterate over selection table list in steps of 2 (waveform part + spectrogram part)
        invalid = []
        for i in range(0, len(lines), 2):
            prefix = 1 if lines[i][-1][0] == '-' else 0
            if lines[i][-1][prefix:] not in ['p1', 'p2', 'p3']:
                label = lines[i][-1][prefix:].rstrip(digits)
            else:
                label = lines[i][-1][prefix:]
            if label in transition_matrix.keys():
                content["onset"].append(float(lines[i][3]))
                content["offset"].append(float(lines[i][4]))
                content["cluster"].append(transition_matrix[label])
            else:
                invalid.append(label)
        if len(invalid) > 0:
            logging.warning(f"Invalid labels found in {p}: {sorted(set(invalid))}. These have been ignored in the output file.")
        if output_path == "":
            new_path = p.parent.absolute()
        else:
            new_path = output_path
        # removes ".Table.1.selections.txt" from the end of the file name
        new_path = join(new_path, p.stem.split('.')[0] + '.json')
        completed_files[new_path] = content
        files += 1

    smallest_segment = min([content["min_segment_length"] for content in completed_files.values()])
    for file_name, content in completed_files.items():
        # unify min_segment_length across all files
        content["min_segment_length"] = smallest_segment
        # if chosen, merge all annotations into 1 target class
        if merge_targets:
            content['cluster'] = ['target' if label != 'vocal' else 'vocal' for label in content['cluster']]
        with open(file_name, "w") as fp:
            json.dump(content, fp, indent=2)
    print(f"Processed {files} files.")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Prepares Raven selection tables for WhisperSeg use: convert to .json and add some more info")
    parser.add_argument("-p", "--file_path", type=str, help="Path to .txt selection table files", required=True)
    parser.add_argument("-c", "--config_path", type=str, help="Path to the config file detailing all annotation classes", default='./config/classes.yaml')
    parser.add_argument("-a", "--convert_annotations", choices=['none', 'parent', 'animal', 'parent_filter_replace', 'animal_filter_replace', 'parent_filter_drop', 'animal_filter_drop'], nargs="?", const="none", default="none", help="Whether to abstract annotations into their parent classes or leave them unchanged. \'none\' uses all annotations as provided, \'parent\' converts all child annotations into their parent class, \'animal\' converts all annotations to \"vocal\". \'x_filter_replace\' only converts labels that do not match any filter. \'x_filter_drop\' only converts labels that match a filter and drops the rest. Defaults to %(default)s.",)
    parser.add_argument("-f", "--filter", nargs="+", default=None, metavar='string', help="List of allowed labels to use")
    parser.add_argument("--merge_targets", action="store_true", help="Merge all non-\"vocal\" annotations into a single \"target\" group.")
    parser.add_argument("-s", "--species", type=str, help="The species in the audio, e.g., \"zebra_finch\" When adding new species, go to the WhisperSeg load_model() function in model.py, add a new pair of species_name:species_token to the species_codebook variable. E.g., \"catta_lemur\":\"<|catta_lemur|>\".", default='catta_lemur')
    parser.add_argument("-d", "--clip_duration", type=float, help="Length D of the audio clips each file will be divided into by the algorithm. Used here to compute hop length L and spec_time_step.", default=2.5)
    parser.add_argument("-m", "--min_frequency", type=int, help="The minimum frequency when computing the Log Melspectrogram. Frequency components below min_frequency will not be included in the input spectrogram.", default=0)
    parser.add_argument("-t", "--tolerance", type=float, help="When computing the F1_seg score, we need to check if both the absolute difference between the predicted onset and the ground-truth onset and the absolute difference between the predicted and ground-truth offsets are below a tolerance (in seconds)", default=0.5)
    parser.add_argument("-i", "--time_per_frame", type=float, help="The time bin size (in second) used when computing the F1_frame score.", default=0.001)
    parser.add_argument("-e", "--epsilon", type=float, help="The threshold epsilon_vote during the multi-trial majority voting when processing long audio files", default=0.02)
    parser.add_argument("-o", "--output_path", type=str, help="Path to the output .json file. Defaults to the input directory.", default="")
    args = parser.parse_args()

    make_json(**vars(args))