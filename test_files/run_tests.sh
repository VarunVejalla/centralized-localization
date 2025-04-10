#!/bin/bash

rm -f *.gcov *.gcda
rm -rf passing_dir failing_dir
mkdir -p passing_dir failing_dir

gcc -w -fprofile-arcs -ftest-coverage -o $1 $1.c

while IFS=',' read -ra array; do
  test+=("${array[0]}")
  result+=("${array[1]}")
done < tests.csv  

for i in `seq 1 ${#test[@]}`
do
    rm -f *.gcov *.gcda

    if ./$1  ${test[$i-1]} | grep -q "${result[$i-1]/ /}"; then
        # echo "$i: P"
        gcov $1.c > /dev/null 2>&1
        cp $1.c.gcov passing_dir/$1_test${i}.gcov
    else
        # echo "$i: F"
        gcov $1.c > /dev/null 2>&1
        cp $1.c.gcov failing_dir/$1_test${i}.gcov
    fi
done
rm -f *.gcov *.gcda *.gcno $1