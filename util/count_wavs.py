import argparse
from pathlib import Path

def convert_bytes(num: int) -> int:
    """Converts bytes to KB, MB, GB, TB as needed.

    Args:
        num (int): The number of bytes to convert.

    Returns:
        int: The converted number of bytes.
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0

def count_files(path: str, name_filter: str) -> int:
    """Recursively counts the number of files with a specific name in a directory.

    Args:
        path (str): The directory path to search.
        name_filter (str): The filter for possible files to count. Example '*.wav'.

    Returns:
        int: The number of files with the specific name.
    """
    count = 0
    count = len([*Path(path).rglob(name_filter)])
    # size = sum([f.stat().st_size for f in Path(r'/usr/users/bhenne/projects/whisperseg/data').rglob('*.wav')])
    # print(convert_bytes(size))
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count files with a specific name in a directory.")
    parser.add_argument("-p", "--path", help="the directory path to search", required=True)
    parser.add_argument("-f", "--name_filter", help="filter for the files to count", required=True)
    args = parser.parse_args()

    file_count = count_files(args.path, args.file_name)
    print(f"Number of files named '{args.file_name}': {file_count}")
