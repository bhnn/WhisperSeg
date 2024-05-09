from os import environ
from pathlib import Path
from typing import Generator, List


def is_scheduled_job() -> bool:
    """
    Check if this script is running in a scheduled SLURM environment. Interactive sessions will return False.

    Returns:
        bool: True if the script is running as a scheduled job, False otherwise
    """
    if environ.get("SLURM_JOB_ID", None) and environ.get("SLURM_JOB_NAME", None) != "bash":
        return True
    return False

def get_flex_file_iterator(file_path: str, rglob_str: str = "*.txt") -> Generator[Path, None, None] | List[str] | None:
    """
    If the provided path is a directory: Recursively search for .txt files in it and return a generator of Path objects.
    If the provided path is a file: Return a list containing the file path.
    If the provided path does not exist: Return None.

    Args:
        file_path (str): Path to the directory to search
        rglob_str (str, optional): . Defaults to "*.txt".

    Raises:
        ValueError: If the file path is invalid

    Returns:
        Generator[Path, None, None]: If the provided path is a directory, return a generator to traverse it
        List[str]: If the provided path is a file, return a list containing the file path
        None: If the provided path is does not exist, return None
    """
    if not (p := Path(file_path)).exists:
        return None
    else:
        if p.is_file():
            return [Path(file_path)]
        elif p.is_dir():
            return p.rglob(rglob_str)
        else:
            raise ValueError(f"Invalid file path: {file_path}")

def compute_annotation_metadata(duration: float = None, sampling_rate: int = None, l_hop: float = None) -> float:
    """
    Given duration and sampling_rate: Compute the hop length of the spectrogram.
    Given duration and hop length: Compute the sampling rate of the audio file.
    Given sampling rate and hop length: Compute the audio clip duration.
    For specifics, refer to: https://doi.org/10.1101/2023.09.30.560270

    Args:
        duration (float, optional): Audio clip duration in seconds in Hz (not kHz). Defaults to None.
        sampling_rate (int, optional): Sampling rate of the audio file. Defaults to None.
        l_hop (float, optional): Spectrogram hop length. Defaults to None.

    Returns:
        float: The computed value
    """
    if duration and sampling_rate and not l_hop:
        return (duration * sampling_rate) / 1000
    elif duration and l_hop and not sampling_rate:
        return int((l_hop * 1000) / duration)
    elif sampling_rate and l_hop and not duration:
        return (l_hop * 1000) / sampling_rate
    else:
        raise ValueError("Invalid input. Provide two of the three arguments: duration, sampling_rate, l_hop")

def compute_spec_time_step(sampling_rate: int, l_hop: float) -> float:
    """
    Compute the spect_time_step parameter given the sampling rate and hop length.
    For specifics, refer to: https://github.com/bhnn/whisperseg/blob/master/docs/DatasetProcessing.md

    Args:
        sampling_rate (int): Sampling rate of the audio file in Hz (not kHz)
        l_hop (float): Spectrogram hop length

    Returns:
        float: The computed value
    """
    return l_hop / sampling_rate

class EarlyStopHandler:
    # adapted from: https://stackoverflow.com/a/73704579
    def __init__(self, patience: int = 10) -> None:
        """Initializes the EarlyStopHandler object.

        Args:
            patience (int, optional): The amount of epochs without improvement before stopping. Defaults to 10.
        """
        self.patience = patience
        self.counter = 0
        self.max_validation_score = 0

    def check(self, validation_score: float) -> bool:
        """Check if the training should be stopped early based on the validation loss.

        Args:
            validation_score (float): Validation score

        Returns:
            bool: True if the training should be stopped, False otherwise
        """
        if validation_score > self.max_validation_score:
            self.max_validation_score = validation_score
            self.counter = 0
        elif validation_score < self.max_validation_score:
            self.counter += 1
            if self.counter >= self.patience:
                return True
        return False