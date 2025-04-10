#!/bin/bash

# Clean up old coverage data and binaries
rm -rf coverage_output/passing coverage_output/failing
rm -f gol.gcda gol.gcno gol

# Compile with coverage flags
gcc -w -fprofile-arcs -ftest-coverage -o gol gol.c

# Create output directories for test results
mkdir -p coverage_output/passing
mkdir -p coverage_output/failing

# Load test cases from CSV: each line: size,steps,seed,expected_result
size=()
steps=()
seed=()
result=()
while IFS=',' read -ra array; do
  size+=("${array[0]}")
  steps+=("${array[1]}")
  seed+=("${array[2]}")
  result+=("${array[3]}")
done < gol_tests.csv

# Run tests
for ((i = 0; i < ${#size[@]}; i++)); do
    rm -f *.gcov *.gcda

    input="${size[$i]} ${steps[$i]} ${seed[$i]}"
    expected=$(echo -n "${result[$i]}" | tr -d '[:space:]')
    output=$(./gol $input | tr -d '[:space:]')

    if [ "$output" == "$expected" ]; then
        echo "Test $((i + 1)): Passed"
        gcov gol.c > /dev/null 2>&1
        cp gol.c.gcov coverage_output/passing/gol_test$((i + 1)).gcov
    else
        echo "Test $((i + 1)): Failed"
        gcov gol.c > /dev/null 2>&1
        cp gol.c.gcov coverage_output/failing/gol_test$((i + 1)).gcov
    fi
done
