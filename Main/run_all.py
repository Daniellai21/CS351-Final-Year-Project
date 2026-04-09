"""
Run the full fraud detection pipeline end-to-end.
Steps: Simulation -> Data Prep -> Attack -> Retraining
"""
import subprocess
import sys

steps = [
    ("Step 1: Generating synthetic transactions...", "run_simulation.py"),
    ("Step 2: Preparing data and engineering features...", "data_prep.py"),
    ("Step 3: Running evasion attacks...", "run_attack.py"),
    ("Step 4: Running iterative retraining loop...", "run_retraining.py"),
]

for label, script in steps:
    print(f"\n{'='*60}")
    print(label)
    print('='*60)
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"ERROR: {script} failed with exit code {result.returncode}")
        sys.exit(1)

print(f"\n{'='*60}")
print("Pipeline complete. Results saved to results/")
print("Run the notebooks in notebooks/ for visualisations.")
print('='*60)