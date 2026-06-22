import pandas as pd
df = pd.read_csv('results/retraining_results.csv')
pivot = df.groupby(['round','attacker'])['recall'].mean().unstack('attacker')
print(pivot.round(8))