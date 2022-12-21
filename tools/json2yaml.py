import argparse
import json
import os
from pathlib import Path

import yaml


def json2yaml(fname):
    with open(fname, encoding='utf8') as f:
        try:
            data = json.load(f)
            fn, _ = os.path.splitext(fname)
            new_fname = os.path.join(args.output, "{}.yaml".format(fn))

            parent_folder = Path(new_fname).parent
            if not os.path.exists(parent_folder):
                os.makedirs(parent_folder)

            with open(new_fname, 'w', encoding='utf8') as f1:
                yaml.dump(data, f1, allow_unicode=True, sort_keys=False)
        except json.JSONDecodeError:
            return False
    return True


def process_dir(dir_name):
    for root, dirs, files in os.walk(dir_name):
        for fn in files:
            json2yaml(os.path.join(root, fn))
        for dn in dirs:
            process_dir(os.path.join(root, dn))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True,
                        help="Input file(s) and/or folder(s), comma-separated, if multiple")
    parser.add_argument('-o', '--output', type=str, required=True,
                        help="Output folder")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    fs_objects = [x.strip() for x in args.input.split(",")]

    for fs_obj in fs_objects:
        if os.path.isfile(fs_obj):
            json2yaml(fs_obj)
        elif os.path.isdir(fs_obj):
            process_dir(fs_obj)
