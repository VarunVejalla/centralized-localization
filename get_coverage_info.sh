#!/bin/bash


if [ -d "coverage_output/$1_passing" ]; then
    rm -rf coverage_output/$1_passing
fi
if [ -d "coverage_output/$1_failing" ]; then
    rm -rf coverage_output/$1_failing
fi

if [ -f "$1.gcda" ]; then
    rm -f $1.gcda
fi

if [ -f "$1.gcno" ]; then
    rm -f $1.gcno
fi

if [ -f "$1" ]; then
    rm -f $1
fi

gcc -w --coverage -o $1 test_files/$1.c

mkdir coverage_output/$1_passing
mkdir coverage_output/$1_failing

while IFS=',' read -ra array; do
  test+=("${array[0]}")
  result+=("${array[1]}")
done < test_files/tests.csv

for i in `seq 1 ${#test[@]}`
do
    # output=$(./tcas$1 ${test[$i-1]} | xargs)
    # expected=$(echo "${result[$i-1]}" | xargs)
    # if ./tcas$1  ${test[$i-1]} | grep -q "${result[$i-1]/ /}"; then
    #     echo $i:P

    if [ -f "$1.gcda" ]; then
        rm -f $1.gcda
    fi


    output=$(./$1 ${test[$i-1]})
    
    
    if grep -q "$(tr -d '[:space:]' <<< "${result[$i-1]}")" <<< "$output"; then
        # echo $i:P
        gcov test_files/$1.c -o . > /dev/null
        mv $1.c.gcov coverage_output/$1_passing/$1.c_$i.gcov
    else
        gcov test_files/$1.c -o . > /dev/null
        mv $1.c.gcov coverage_output/$1_failing/$1.c_$i.gcov
    fi
done

if [ -f "$1.gcda" ]; then
    rm -f $1.gcda
fi

if [ -f "$1.gcno" ]; then
    rm -f $1.gcno
fi

if [ -f "$1" ]; then
    rm -f $1
fi