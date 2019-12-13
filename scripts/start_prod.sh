#!/bin/bash
# shellcheck disable=SC2046
export $(grep -v '^#' /home/ubuntu/bots/myblumbot_backup/.env | xargs)
"$ROOT_DIR"/scripts/create_folders.sh
"$ROOT_DIR"/venv/bin/python "$ROOT_DIR"/bot/main.py
