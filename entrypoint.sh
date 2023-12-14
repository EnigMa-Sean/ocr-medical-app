#!/bin/bash

home_dir=$HOST_ROOT_DIR

FILE_PATH="$home_dir/ocr_data"

if [ -e "$FILE_PATH" ]; then
    :
else

    mkdir -p "$home_dir/ocr_data/csv_reports"
    mkdir -p "$home_dir/ocr_data/templates"

    python main.py
fi

pkill Xvfb

Xvfb :0 -screen 0 1024x768x16 &

export DISPLAY=:0

ps aux | grep Xvfb

# xeyes
# python ./ocr_med/interface/ui_tkinter.py &

exec "$@"