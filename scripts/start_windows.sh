#!/bin/bash
# shellcheck disable=SC2046
export $(grep -v '^#' /d/bot_projects/myblumbot_backup/.env | xargs)
"$ROOT_DIR"/scripts/create_folders.sh
"$ROOT_DIR"/venv/Scripts/python "$ROOT_DIR"/myblumbot/main.py
