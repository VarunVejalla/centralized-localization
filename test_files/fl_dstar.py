import sys
import os
import glob
import pandas as pd

def parse_gcov_file(filename):
    results = {}
    with open(filename, 'r') as f:
        for line in f:
            # format: exec_count : line_number : statement
            parts = line.split(':')

            exec_count_str = parts[0].strip()
            line_num_str= parts[1].strip()
            statement = parts[2].strip()
            
            line_num = int(line_num_str)

            executed = exec_count_str.isdigit() and int(exec_count_str) > 0

            results[line_num] = (executed, statement)
    return results

passing_dir = sys.argv[1]
failing_dir = sys.argv[2]

passed_counts = {}
failed_counts = {}
statements = {}

passing_files = glob.glob(os.path.join(passing_dir, "*.gcov"))
for gcov_file in passing_files:
    cov_data = parse_gcov_file(gcov_file)
    for line_num, (executed, statement) in cov_data.items():
        if line_num not in statements:
            statements[line_num] = statement
        if executed:
            passed_counts[line_num] = passed_counts.get(line_num, 0) + 1

failing_files = glob.glob(os.path.join(failing_dir, "*.gcov"))
total_failed = len(failing_files)
for gcov_file in failing_files:
    cov_data = parse_gcov_file(gcov_file)
    for line_num, (executed, statement) in cov_data.items():
        if line_num not in statements:
            statements[line_num] = statement
        if executed:
            failed_counts[line_num] = failed_counts.get(line_num, 0) + 1

results = []
for line_num, stmt in statements.items():
    failed = failed_counts.get(line_num, 0)
    passed = passed_counts.get(line_num, 0)
    denominator = passed + total_failed - failed
    if denominator == 0:
        suspiciousness = 0
    else:
        suspiciousness = (failed ** 2) / denominator
    results.append((line_num, stmt, failed, passed, total_failed, suspiciousness))

results.sort(key=lambda x: (-x[5], x[0]))

df = pd.DataFrame(results, columns=["Line", "Statement", "#failedTests(s)", "#passedTests(s)", "totalFailed", "Suspiciousness"])

width = 30
df["Statement"] = df["Statement"].apply(lambda s: s.replace("\t", " " * 4))
df["Statement"] = df["Statement"].apply(lambda s: s if len(s) <= width else s[:width - 4] + " ...")

df["Suspiciousness"] = df["Suspiciousness"].apply(lambda x: f"{x:.2f}")

print(df.head(10).to_string(index=False))
