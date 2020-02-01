#!/bin/bash
# shellcheck disable=SC2046
export $(grep -v '^#' /root/myblumbot/.env | xargs)
"$ROOT_DIR"/scripts/create_folders.sh
"$ROOT_DIR"/venv/bin/python "$ROOT_DIR"/myblumbot/main.py