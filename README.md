# centralized-localization

to get CFG with line numbers:

gcc -O0 -fdump-tree-cfg-graph-lineno -c quicksort.c -o /dev/null

1. get CFG
2. separate blocks in CFG with multiple lines
3. combine adjacent blocks (with no branching shenanigans) on same line?
4. get test coverage for each line
5. assign test coverage to blocks