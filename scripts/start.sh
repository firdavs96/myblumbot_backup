#!/bin/bash
# shellcheck disable=SC2046
export $(grep -v '^#' /media/amarus/DATA/Programming/Bots/myblumbot_backup/.env | xargs)
"$ROOT_DIR"/scripts/create_folders.sh
"$ROOT_DIR"/venv/bin/python "$ROOT_DIR"/myblumbot/main.py
