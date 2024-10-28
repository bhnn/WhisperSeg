import argparse
import json
from copy import deepcopy
from os.path import join
from pathlib import Path

import numpy as np
from common import get_flex_file_iterator
from scipy.io import wavfile

"""
- start at 0
- look at distance between offset 0 - onset 1
- if shorter than 0, look at 1 - 2, continue
- if longer, clip after offset 1
- randomised padding, front/back, [0.25*distance, 0.49*distance]
- start after previous cut-off, repeat
"""

def clip_fragment(wav_file: str, num_fragments: int, onset: float, offset: float, pre_distance: float, post_distance: float, output_dir: str, max_distance: float = 15) -> float:
    """Clips a fragment from a .wav file and writes it to a new file.

    Args:
        wav_file (str): Path to a .wav file
        num_fragments (int): Counter for the number of fragments created so far
        onset (float): Onset timestamp of first call in this fragment
        offset (float): Offset timestamp of last call in this fragment
        pre_distance (float): Distance to the previous call
        post_distance (float): Distance to the next call
        output_dir (str): Path to output directory
        max_distance (float, optional): Maximum distance to the next call. Defaults to 15.

    Returns:
        float: Amount of padding added to the start of the .wav file
    """
    sampling_rate, data = wavfile.read(wav_file)
    max_frames = len(data)

    if pre_distance > max_distance:
        pre_pad = np.random.uniform(low=0.33, high=0.5) * max_distance
    else:
        pre_pad = np.random.uniform(low=0.33, high=0.5) * pre_distance
    if post_distance > max_distance:
        post_pad = np.random.uniform(low=0.33, high=0.5) * max_distance
    else:
        post_pad = np.random.uniform(low=0.33, high=0.5) * pre_distance

    # Calculate cut-off frames plus randomised padding
    start_frame = int(max(onset * sampling_rate - (pre_pad * sampling_rate), 0))
    end_frame = int(min(offset * sampling_rate + (post_pad * sampling_rate), max_frames))

    trimmed_data = data[start_frame:end_frame]
    new_file_name = join(output_dir, Path(wav_file).stem + f'_seg_{num_fragments:03}.wav')
    wavfile.write(new_file_name, sampling_rate, trimmed_data)
    return pre_pad

def clip_json(json_file: str, num_fragments: int, onset_idx: int, offset_idx: int, padding: float, output_dir: str):
    """Loads a .json file, clips the data to the specified indices, and writes the new data to a new .json file.

    Args:
        json_file (str): Path to a .json file
        num_fragments (int): Counter for the number of fragments created so far
        onset_idx (int): First index to include in the new .json fragment
        offset_idx (int): Last index to include in the new .json fragment
        padding (float): Tracker for the amount of padding added to the start of the corresponding .wav file
        output_dir (str): Path to output directory
    """
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    new_json = deepcopy(json_data)
    new_json['onset'] = new_json['onset'][onset_idx:offset_idx+1]
    new_json['offset'] = new_json['offset'][onset_idx:offset_idx+1]
    new_json['cluster'] = new_json['cluster'][onset_idx:offset_idx+1]
    new_json['trimmed_seg_onset'] = new_json['onset'][0] - padding
    zero = new_json['trimmed_seg_onset']
    for i in range(len(new_json['onset'])):
        new_json['onset'][i] = new_json['onset'][i] - zero
        new_json['offset'][i] = new_json['offset'][i] - zero
    new_file_name = join(output_dir, Path(json_file).stem + f'_seg_{num_fragments:03}.json')
    with open(new_file_name, "w") as fp:
        json.dump(new_json, fp, indent=2)

def find_gaps(file_path: str, max_silence: int, output_dir: str) -> None:
    """Find gaps larger than max_silence seconds between calls in a audio file and splits it into fragments that contain
       a more balanced amount of calls to background noise. Looks in the file_path directory for .json files to read out
         the call onsets and offsets, then looks for the corresponding .wav files in the same directory.

    Args:
        file_path (str): Path to directory containing .wav and .json files
        max_silence (int): Longest permitted interval between two calls, in seconds.
        output_dir (str): Path to output directory
    """
    for fpath in get_flex_file_iterator(file_path, rglob_str='*.json'):
        with open(fpath, 'r') as f:
            json_data = json.load(f)
        print(fpath)
        start = 0 # tracks start index of current fragment
        num_fragments = 0 # tracks number of fragments found so far
        i = 0 # start <= i, increments until new fragment border is found
        while i < len(json_data['onset']) - 1:
            if abs(json_data['offset'][i] - json_data['onset'][i+1]) > max_silence:
                print(f'{start:>3} - {i:>3}: ({json_data["onset"][i+1]:.3f})')
                pre_pad = clip_fragment(
                    wav_file=join(fpath.parent, fpath.stem + '.wav'),
                    num_fragments=num_fragments,
                    onset=json_data['onset'][start],
                    offset=json_data['offset'][i],
                    pre_distance=(abs(json_data['offset'][start-1] - json_data['onset'][start]) if start > 1 else 1), # else 1 = safety padding from trim_wavs.py
                    # pre_distance=(abs(json_data['offset'][i-1] - json_data['onset'][i]) if i > 1 else 1),
                    post_distance=abs(json_data['offset'][i] - json_data['onset'][i+1]),
                    output_dir=output_dir,
                )
                clip_json(
                    json_file=fpath,
                    num_fragments=num_fragments,
                    onset_idx=start,
                    offset_idx=i,
                    padding=pre_pad,
                    output_dir=output_dir,
                )
                start = i+1
                num_fragments += 1
            i += 1
        if start < len(json_data['onset']):
            pre_pad = clip_fragment(
                wav_file=join(fpath.parent, fpath.stem + '.wav'),
                num_fragments=num_fragments,
                onset=json_data['onset'][start],
                offset=json_data['offset'][len(json_data['onset'])-1],
                pre_distance=(abs(json_data['offset'][start-1] - json_data['onset'][start]) if start > 1 else 1),
                post_distance=float('inf'), # any length, clip_fragment checks for end-of-file
                output_dir=output_dir,
            )
            clip_json(
                json_file=fpath,
                num_fragments=num_fragments,
                onset_idx=start,
                offset_idx=len(json_data['onset']),
                padding=pre_pad,
                output_dir=output_dir,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Finds gaps larger than \'-s\' seconds between calls in a audio file and splits it into fragments that contain a more balanced amount of calls to background noise.")
    parser.add_argument("-p", "--file_path", type=str, help="Path to directory containing .wav and .json files", required=True)
    parser.add_argument("-s", "--max_silence", type=int, help="Longest permitted interval between two calls, in seconds.", required=True)
    parser.add_argument("-o", "--output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    find_gaps(**vars(args))