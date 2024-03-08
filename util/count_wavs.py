import argparse
from pathlib import Path

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0

def count_files(path, file_name):
    count = 0
    count = len([*Path(path).rglob(file_name)])
    # size = sum([f.stat().st_size for f in Path(r'E:\\dpz\\all_data').rglob('*.wav')])
    # print(convert_bytes(size))
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count files with a specific name in a directory.")
    parser.add_argument("-p", "--path", help="the directory path to search", required=True)
    parser.add_argument("-f", "--file_name", help="the name of the file to count", required=True)
    args = parser.parse_args()

    file_count = count_files(args.path, args.file_name)
    print(f"Number of files named '{args.file_name}': {file_count}")
