#!/usr/bin/env python
import os
import re

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.unlink(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == "__main__":
    # if use_makefile != 'yes', remove Makefile
    if not re.match(r"(?i)^\s*(y(es)?|1|t(rue)?)\s*$", "{{cookiecutter.use_makefile}}"):
        remove_file("Makefile")
