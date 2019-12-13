#!/bin/bash
# shellcheck disable=SC2046
export $(grep -v '^#' /media/amarus/DATA1/Programming/Bots/myblumbot_backup/.env | xargs)
"$ROOT_DIR"/scripts/create_folders.sh
"$ROOT_DIR"/venv/bin/python "$ROOT_DIR"/myblumbot/main.py 1>>"$ROOT_DIR"/logs/out.log 2>>"$ROOT_DIR"/logs/err.log
