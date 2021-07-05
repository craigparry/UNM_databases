#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True

import os
import json


def create_file(filename, content=""):
    file_dir = os.path.dirname(os.path.normpath(filename))
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)

    with open(filename, "w") as file:
        if isinstance(content, str):
            file.write(content)
        elif isinstance(content, dict):
            file.write(json.dumps(content))
        elif isinstance(content, list):
            file.writelines(content)


def json_to_dict(json_file):
    with open(json_file, "r") as jf:
        content = jf.readlines()[1:]
        json_content = ""
        for entry in content:
            json_content += entry
    return json.loads(json_content)
