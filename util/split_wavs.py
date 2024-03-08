import argparse
import os

from pydub import AudioSegment


def split_wavs(path):
    """
    Splits .wav files in half

    Args:
        path (str): Path to the directory containing the files to split
    """
    wav_files = [file for file in os.listdir(path) if file.endswith(".wav")]

    for f in wav_files:
        # Load the audio file
        audio = AudioSegment.from_wav(os.path.join(path, f))

        # Split the audio file in half
        print(len(audio) / 1000)
        halfway_point = len(audio) // 2
        first_half = audio[:halfway_point]
        second_half = audio[halfway_point:]

        # Save halves with different names
        first_half.export(os.path.join(path, f + '_first'), format="wav")
        second_half.export(os.path.join(path, f + '_second'), format="wav")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Splits .wav files in half")
    parser.add_argument("-p", "--path", type=str, help="Path to the .wav files", required=True)
    args = parser.parse_args()

    split_wavs(args.path)
