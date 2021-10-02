#!/usr/bin/env bash

PROJECT_NAME="spb_ai_champ"
SOLUTION_CODE_ENTRYPOINT="my_strategy.py"
function compile() (
    set -e
    zip -r - . > /tmp/$PROJECT_NAME.zip
)
COMPILED_FILE_PATH="/tmp/$PROJECT_NAME.zip"
function run() (
    set -e
    unzip $MOUNT_POINT -d /tmp/project >/dev/null
    cd /tmp/project
    python main.py "$@"
)

. codegame.sh