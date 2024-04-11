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