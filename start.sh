#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Starting bustracker"
# Simple script to keep running bustracker
while :
do
    clear
    $SCRIPT_DIR/bustracker.py
    sleep 60s
done
