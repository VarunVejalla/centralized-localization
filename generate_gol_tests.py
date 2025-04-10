import subprocess
import random
import csv
import os

# Path to compiled C program
EXECUTABLE = "./gol"
CSV_FILE = "gol_tests.csv"
NUM_TESTS = 100

if not os.path.exists(EXECUTABLE):
    raise FileNotFoundError(f"Executable not found: {EXECUTABLE}")

def generate_random_test():
    size = random.randint(5, 20)
    steps = random.randint(1, 10)
    seed = ''.join(random.choices('01', k=size * size))
    return size, steps, seed

def run_test(size, steps, seed):
    try:
        result = subprocess.run(
            [EXECUTABLE, str(size), str(steps), seed],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        output = result.stdout.strip()
        if len(output) == size * size and all(c in '01' for c in output):
            return output
        else:
            print(f"Unexpected output for size={size}, steps={steps}:\n{output}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running test: {e.stderr}")
        return None

def append_to_csv(filename, data):
    exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["size", "steps", "seed", "output"])
        writer.writerows(data)


all_results = []
for _ in range(NUM_TESTS):
    size, steps, seed = generate_random_test()
    output = run_test(size, steps, seed)
    if output:
        all_results.append((size, steps, seed, output))
    else:
        print(f"ERROR")
append_to_csv(CSV_FILE, all_results)

