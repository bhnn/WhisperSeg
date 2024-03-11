import argparse
import json
import logging
from os.path import join
from pathlib import Path

import librosa

from model import WhisperSegmenterFast


def infer(data_dir: str, model_path: str, output_dir: str, sampling_rate: int, min_frequency: int, spec_time_step: float, min_segment_length: float, eps: float, num_trials: int):
    """
    Use a trained WhisperSeg checkpoint to segment a data file and compute inference values.

    Args:
        data_dir (str): The path to the directory containing audio files to be segmented
        model_path (str): The path to the trained model checkpoint
        output_dir (str): The path to the directory where the output files will be saved
        sampling_rate (int): Sampling rate of the audio files
        min_frequency (int): Minimum frequency for computing the Log Melspectrogram. Components below min_frequency will not be included in the input spectrogram.
        spec_time_step (float): Spectrogram Time Resolution. By default, one single input spectrogram of WhisperSeg contains 1000 columns.
        min_segment_length (float): The minimum allowed length of predicted segments. The predicted segments whose length is below 'min_segment_length' will be discarded.
        eps (float): The threshold epsilon_vote during the multi-trial majority voting when processing long audio files
        num_trials (int): Number of trials
    """
    segmenter = WhisperSegmenterFast(model_path, device="cuda")
    for p in Path(data_dir).rglob('*.wav'):
        logging.info(f"Current file: {p}")
        
        audio_file = p
        audio, _ = librosa.load(audio_file, sr=sampling_rate)

        prediction = segmenter.segment(
            audio,
            sr=sampling_rate,
            min_frequency=min_frequency,
            spec_time_step=spec_time_step,
            min_segment_length=min_segment_length,
            eps=eps,
            num_trials=num_trials
        )
        if output_dir == None:
            new_path = p.parent.absolute()
        else:
            new_path = output_dir
        out_path = join(new_path, p.stem + '.jsonr')
        with open(out_path, "w") as fp:
            json.dump(prediction, fp=fp, indent=2)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Use a trained WhisperSeg checkpoint to segment a data file and compute inference values.")
    parser.add_argument("-d", "--data_dir", type=str, help="Path to a directory containing audio files to be segmented", required=True)
    parser.add_argument("-m", "--model_path", type=str, help="Path to the trained model checkpoint", required=True)
    parser.add_argument("-o", "--output_dir", type=str, help="Path to a directory where the output files will be saved", default=None)
    parser.add_argument("-s", "--sampling_rate", type=int, help="Sample rate of the audio files", default=48000)
    parser.add_argument("-f", "--min_frequency", type=int, help="Minimum frequency", default=0)
    parser.add_argument("-t", "--spec_time_step", type=float, help="Spectrogram time step", default=0.0025)
    parser.add_argument("-l", "--min_segment_length", type=float, help="Minimum segment length", default=0.0245)
    parser.add_argument("-e", "--eps", type=float, help="Epsilon", default=0.02)
    parser.add_argument("-n", "--num_trials", type=int, help="Number of trials", default=3)
    args = parser.parse_args()

