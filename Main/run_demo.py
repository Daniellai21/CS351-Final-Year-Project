import subprocess
import sys

W = 65

def banner(title, subtitle=""):
    print()
    print("=" * W)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * W)

def section(text):
    print(f"\n  -> {text}")

def done(script):
    print(f"\n  [OK] {script} completed successfully.")
    print("-" * W)

# ── INTRO ──────────────────────────────────────────────────────────────────────

banner(
    "ADVERSARIAL ROBUSTNESS OF ML-BASED FRAUD DETECTION SYSTEMS",
    "CS351 Final Year Project  |  Live Pipeline Demo"
)
print()
print("  This demo runs the complete 4-stage evaluation pipeline:")
print("  Simulation -> Feature Engineering -> Attack -> Retraining")
print()
print("  Framework: Stackelberg game (defender commits first, attacker responds)")
print("  Defenders: Logistic Regression, Random Forest, XGBoost")
print("  Attackers: 5 static strategies + Score-Aware Adaptive Attacker")
print()

# ── STEP 1: SIMULATION ────────────────────────────────────────────────────────

banner(
    "STEP 1 of 4: Synthetic Transaction Simulation",
    "run_simulation.py"
)
section("Generating synthetic credit card transactions for 560 users over 90 days")
section("5 user personas: Commuter, Student, Homebody, Professional, Retiree")
section("Each persona has distinct spending patterns (amount, time-of-day, category)")
section("Fraud injected at 2% rate across 8 campaign types")
print()

result = subprocess.run([sys.executable, "run_simulation.py"])
if result.returncode != 0:
    print(f"\n  ERROR: run_simulation.py failed (exit code {result.returncode})")
    sys.exit(1)
done("run_simulation.py")
section("Output saved -> data/synthetic_transactions_v2.csv")

# ── STEP 2: DATA PREP ─────────────────────────────────────────────────────────

banner(
    "STEP 2 of 4: Feature Engineering & Train/Test Split",
    "data_prep.py"
)
section("Computing 8 user-relative temporal features (no future data leakage)")
section("Features: amount_zscore, transactions_last_1h, amount_sum_last_24h,")
section("          log_time_since_last_txn, is_new_category, is_foreign,")
section("          hour_of_day, is_night")
section("Splitting 80/20 by timestamp (chronological - no random shuffle)")
print()

result = subprocess.run([sys.executable, "data_prep.py"])
if result.returncode != 0:
    print(f"\n  ERROR: data_prep.py failed (exit code {result.returncode})")
    sys.exit(1)
done("data_prep.py")
section("Output saved -> data/raw_train_transactions.csv")
section("             -> data/raw_test_transactions.csv")
section("             -> data/featured_transactions_v2.csv")

# ── STEP 3: EVASION ATTACKS ───────────────────────────────────────────────────

banner(
    "STEP 3 of 4: Applying Evasion Attack Strategies",
    "run_attack.py"
)
section("Applying 5 static evasion attacks to the test set:")
section("  Amount Scaling   - scales transaction amounts to blend into normal spend")
section("  Time Shift       - shifts timestamps to exploit time-of-day features")
section("  Category Mimicry - changes merchant category to match user's normal behaviour")
section("  Velocity Spacing - adds artificial gaps between transactions to beat velocity checks")
section("  Combined         - chains all 4 strategies simultaneously (strongest static attack)")
section("Attack operates at inference time only - training data is untouched")
print()

result = subprocess.run([sys.executable, "run_attack.py"])
if result.returncode != 0:
    print(f"\n  ERROR: run_attack.py failed (exit code {result.returncode})")
    sys.exit(1)
done("run_attack.py")
section("Output saved -> data/attacked_transactions_<attacker>.csv  (one file per attacker)")

# ── STEP 4: ITERATIVE RETRAINING ─────────────────────────────────────────────

banner(
    "STEP 4 of 4: Stackelberg Game - Iterative Retraining Loop",
    "run_retraining.py"
)
section("Simulating 8 rounds of the Stackelberg game:")
section("  Round N: Defender evaluates on attacked holdout -> records F1/Recall/AUC")
section("         : Defender detects attacks in feedback set -> retrains on augmented data")
section("         : Attacker (static) stays fixed; Score-Aware Attacker updates each round")
section("Isolated state per (attacker, model) pair - no cross-contamination between timelines")
section("Equilibrium detection: recall change < 0.5% between rounds triggers early stop")
section("Score-Aware Adaptive Attacker uses the defender's own probability scores as feedback")
print()

result = subprocess.run([sys.executable, "run_retraining.py"])
if result.returncode != 0:
    print(f"\n  ERROR: run_retraining.py failed (exit code {result.returncode})")
    sys.exit(1)
done("run_retraining.py")
section("Output saved -> results/retraining_results.csv")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────

banner("PIPELINE COMPLETE")
print()
print("  All 4 stages completed successfully.")
print()
print("  Results are saved to:")
print("    results/retraining_results.csv  - F1, Recall, Precision, AUC per round")
print()
print("  Key findings from the full run:")
print("    * Combined attack caused the largest recall drop across all 3 defenders")
print("    * Score-Aware Adaptive Attacker was the most persistent threat")
print("    * Retraining provided partial recovery but could not fully close the gap")
print("    * Stackelberg equilibrium confirmed - game converged")
print()
print("=" * W)