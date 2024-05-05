import argparse
import csv
import json
from datetime import datetime
from os.path import join

from common import get_flex_file_iterator
from scipy.io import wavfile


def trim_wavs(file_path: str, safety_padding: float = 1.0) -> None:
    """Trims unannotated content from front and back of .wav audio recordings in given directory based on their onset and offset times from the associated json files. This overwrites the original .wav files with the trimmed versions and saves information about length of trimmed content to disk.

    Args:
        file_path (str): Path to directory containing .wav and .json files
        safety_padding (float, optional): Extra time to leave as padding at the front and back of the trimmed audio files, in seconds. Defaults to 1.0.
    """
    csv_records = []

    for p in get_flex_file_iterator(file_path, rglob_str="*.wav"):
        # Load the json data
        json_path = join(p.parent.absolute(), p.stem + '.json')
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        onset = json_data['onset'][0]
        offset = json_data['offset'][-1]

        # Load .wav file
        sampling_rate, data = wavfile.read(p)
        max_frames = len(data)

        # Calculate cut-off frames plus some padding for safety
        start_frame = int(max(onset * sampling_rate - (safety_padding * sampling_rate), 0))
        end_frame = int(min(offset * sampling_rate + (safety_padding * sampling_rate), max_frames))

        trimmed_data = data[start_frame:end_frame]
        wavfile.write(p, sampling_rate, trimmed_data)

        json_data['onset'] = [x - onset + safety_padding for x in json_data['onset']]
        json_data['offset'] = [x - onset + safety_padding for x in json_data['offset']]
        json_data['trimmed_onset'] = onset
        with open(json_path, "w") as fp:
            json.dump(json_data, fp, indent=2)

        time_cut_front = onset
        time_cut_back = max_frames / sampling_rate - offset
        csv_records.append([p.parent, p.stem, time_cut_front, time_cut_back])

    # Write the csv information to disk
    csv_file_path = join('results', datetime.now().strftime("%Y%m%d-%H%M%S")+'_meta_info.csv')
    with open(csv_file_path, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Parent Path', 'File Name', 'Time Cut Front', 'Time Cut Back'])
        csv_writer.writerows(csv_records)

    print('Trimming completed successfully!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--file_path", type=str, help="Path to directory containing .wav and .json files", required=True)
    args = parser.parse_args()

    trim_wavs(**vars(args))
