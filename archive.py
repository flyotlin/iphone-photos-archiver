import argparse
import exifread
import os
import shutil

from typing import Tuple


def walk(path: str) -> Tuple[str, list]:
    walk_generator = os.walk(path)
    res = list(next(walk_generator))
    base_path, dir_name = res[0], res[1]

    return base_path, list(map(lambda x: os.path.join(base_path, x), dir_name))


def move_to_tmp(dir_paths: list, tmp_dir: str) -> None:
    for dir in dir_paths:
        if dir == tmp_dir:
            continue
        move_dir(dir, tmp_dir)


def move_dir(src: str, dest: str, flat: bool = True) -> None:
    """Move all contents under src to dest

    Args:
        src (str): src dir path (only content inside would be moved)
        dest (str): _description_
        flat (bool): whether src directory would be flatten
    """
    if not os.path.isdir(dest):
        os.mkdir(dest)

    for dirPath, _, fileNames in os.walk(src):
        for file in fileNames:
            shutil.move(os.path.join(dirPath, file), dest)
        os.rmdir(dirPath)


def move_photo(src: str, year: int, month: int, base_path: str) -> None:
    if year == -1 and month == -1:
        ym_path = os.path.join(base_path, 'others')
    else:
        ym_path = os.path.join(base_path, f'{year}_{month}')

    if not exist_year_month_dir(ym_path):
        make_year_month_dir(ym_path)

    shutil.move(src, ym_path)


def exist_year_month_dir(ym_path: str) -> bool:
    return os.path.isdir(ym_path)


def make_year_month_dir(ym_path: str) -> None:
    os.mkdir(ym_path)


def sort_by_year_month(tmp_dir: str, base_path: str) -> None:
    for _, _, fileNames in os.walk(tmp_dir):
        for file in fileNames:
            with open(os.path.join(tmp_dir, file), 'rb') as f:
                tags = exifread.process_file(f)
                if 'Image DateTime' in tags:
                    ymd = str(tags['Image DateTime']).split(' ')[0].split(':')
                    year, month = ymd[0], ymd[1]
                    move_photo(os.path.join(tmp_dir, file), int(year), int(month), base_path)
                else:
                    move_photo(os.path.join(tmp_dir, file), -1, -1, base_path)


def remove_tmp(tmp_dir: str) -> None:
    os.rmdir(tmp_dir)


def main(args):
    base_path, dir_paths = walk(args.path)
    tmp_dir = os.path.join(base_path, 'tmp')

    move_to_tmp(dir_paths, tmp_dir)

    sort_by_year_month(tmp_dir, base_path)

    remove_tmp(tmp_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True, help='exported images base directory path')
    args = parser.parse_args()

    main(args)
