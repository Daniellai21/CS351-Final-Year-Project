# Robustness Evaluation of ML-Based Fraud Detection Against Evasive Attacks

**CS351 — Computer Systems Engineering Project**  
**Daniel Lai** | University of Warwick | 2025–2026  
**Supervisor:** Long Tran-Thanh

## Overview

This project investigates the robustness of supervised fraud detection models under adversarial evasion attacks, framed as a sequential Stackelberg game. A custom transaction simulator generates realistic card payment data across diverse user personas. Three ML defenders (Logistic Regression, Random Forest, XGBoost) are evaluated against six attack strategies, including an adaptive score-aware adversary, through an iterative retraining loop.

## Setup

It is recommended to run inside a virtual environment:
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt


Note: The `requirements.txt` contains all packages from the development environment. The core dependencies are: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `matplotlib`, `seaborn`, and `joblib`.

## Running the Pipeline

# Run the full pipeline in one command
python run_all.py

# Or run individual steps:
python run_simulation.py
python data_prep.py
python run_attack.py
python run_retraining.py

Results and visualisations can then be explored in the Jupyter notebooks in `notebooks/`.
