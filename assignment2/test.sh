#/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function fail() {
	echo "$1" >/dev/stderr
	exit 1
}

function run() {
	echo "Testing $1 ..."
	python3 ${SCRIPT_DIR}/main.py ${SCRIPT_DIR}/test/$1 > /tmp/output ||: #|| fail "Execution failed for $1"
	if [ "$2" != "$(cat /tmp/output)" ] ; then
		fail "  Wrong result. Expected: \"$2\". Actual: \""$(cat /tmp/output)"\""
	fi
}

###

run basic1.txt	"10"
run basic2.txt	"9"
run basic3.txt	"1118"
run cond1.txt	"10"
run cond2.txt	"2"
run fib.txt 	"610"
run main.txt	"12"
run avg.txt		"5.0"


echo "*** All tests successful! ***"