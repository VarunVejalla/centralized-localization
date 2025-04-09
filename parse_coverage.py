import sys
import os

def parse_file(file):
    lookup = {}
    lines = file.readlines()
    for line in lines:
        splitted = line.strip().split(":", 2)
        if len(splitted) < 3:
            continue
        execs, line_no, statement = splitted
        execs = execs.strip()
        line_no = line_no.strip()
        statement = statement.strip()
        
        if not execs.isnumeric():
            continue
        if not line_no.isnumeric():
            raise Exception('weird line number')
        
        execs = int(execs)
        line_no = int(line_no)
        
        if execs <= 0:
            raise Exception('line executed 0 times')
        
        if line_no in lookup:
            raise Exception('repeated line number')
        
        lookup[line_no] = statement
    
    return lookup

passing_dir = sys.argv[1]
failing_dir = sys.argv[2]

counts = {}
statement_lookup = {}

for i,dir in [(0,passing_dir), (1,failing_dir)]:
    for gcov_file in os.listdir(dir):
        file_name = os.path.join(dir, gcov_file)
        file = open(file_name)
        lookup = parse_file(file)
        file.close()
        
        for line_no in lookup:
            if line_no not in counts:
                counts[line_no] = [0,0]
            
            counts[line_no][i] += 1
            
            if line_no in statement_lookup:
                assert statement_lookup[line_no] == lookup[line_no]
            else:
                statement_lookup[line_no] = lookup[line_no]

print(counts)