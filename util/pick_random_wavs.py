import argparse
import random
import shutil
from os.path import join
from pathlib import Path
from typing import List

from common import get_flex_file_iterator
from tqdm import tqdm


def pick_random_files(file_path: str, output_path: str, num_files: int) -> List:
    """Picks random .wav recordings from passed directory and its subdirectories, then copies them to desired output directory.

    Args:
        file_path (str): Path to directory containing .wav files in itself or its subdirectories
        output_path (str): Path to output directory
        num_files (int): Number of random files to pick

    Returns:
        (List): List of paths to picked files
    """
    files = []
    for f in get_flex_file_iterator(file_path, rglob_str="*.wav"):
        if Path(f).is_file() and Path(f).suffix == '.wav' and Path(f).stat().st_size > (10 * 1024 * 1024): # 10MB
            files.append(f.absolute())

    random_files = random.sample(files, num_files)

    for f in tqdm(random_files, desc="Copying files", unit="file"):
        shutil.copy(f, output_path)

    output_file = join(output_path, "random_files.txt")
    with open(output_file, "w") as f:
        for file in random_files:
            f.write(str(file) + "\n")

    return random_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Picks random .wav recordings from passed directory and its subdirectories, then copies them to desired output directory.")
    parser.add_argument("-p", "--file_path", type=str, help="Path to directory containing .wav files in itself or its subdirectories", required=True)
    parser.add_argument("-o", "--output_path", type=str, help="Path to output directory", required=True)
    parser.add_argument("-n", "--num_files", type=int, help="Number of random files to pick", default=50)
    args = parser.parse_args()

    files = pick_random_files(**vars(args))