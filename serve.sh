#!/bin/bash

HERE=$(dirname "$(realpath -s "$0")")
"$HERE/.venv/bin/python" "$HERE/main.py"
