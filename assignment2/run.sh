#/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DEFAULT_FILE=${SCRIPT_DIR}/test/main.txt

FILE=${1:-$DEFAULT_FILE}

#echo "Running $FILE ..."
python3 ${SCRIPT_DIR}/main.py $FILE
