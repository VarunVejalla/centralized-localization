#!/bin/bash

pip3 install pandas

for i in {0..3}; do
    echo -e "\ntcas$i:"
    ./run_tests.sh "tcas$i"
    python3 fl_dstar.py "$(pwd)/passing_dir" "$(pwd)/failing_dir"
done

