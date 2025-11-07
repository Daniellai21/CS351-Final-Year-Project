# simulator.py

import pandas as pd
import datetime
from personas import Persona  
from personas_profile import COMMUTER_PROFILE, STUDENT_PROFILE 

# INITIALIZING PERSONAS
print("Initializing personas...")
all_personas = []
NUM_COMMUTERS = 10
NUM_STUDENTS = 10

for i in range(NUM_COMMUTERS):
    all_personas.append(
        Persona(user_id=f"USER_C_{1001+i}", 
                card_id=f"CARD_C_{1001+i}_A", 
                profile=COMMUTER_PROFILE)
    )
    
for i in range(NUM_STUDENTS):
    all_personas.append(
        Persona(user_id=f"USER_S_{2001+i}", 
                card_id=f"CARD_S_{2001+i}_A", 
                profile=STUDENT_PROFILE)
    )

all_transactions = []
transaction_id_counter = 1

# SIMULATION LOOP
start_date = datetime.date(2025, 1, 1)
NUM_DAYS = 90
print(f"Starting simulation for {len(all_personas)} personas over {NUM_DAYS} days...")

for day_num in range(NUM_DAYS):
    current_date = start_date + datetime.timedelta(days=day_num)
    
    for persona in all_personas:
        # Tell each persona to simulate its day
        daily_txns, new_counter = persona.simulate_day(current_date, transaction_id_counter)
        
        all_transactions.extend(daily_txns)
        transaction_id_counter = new_counter

print(f"Simulation complete. Generated {len(all_transactions)} total transactions.")

# CREATE AND SAVE DATAFRAME
if all_transactions:
    df = pd.DataFrame(all_transactions)

    # Columns reordering
    column_order = [
        'Transaction_id', 'Timestamp', 'user_id', 'Card_id', 'home_country', 
        'Transaction amount', 'merchant_id', 'merchant_category',
        'merchant_country', 'Channel', 'is_fraud'
    ]
    # Filter to only columns that exist (in case one was missed)
    final_columns = [col for col in column_order if col in df.columns]
    df = df[final_columns]

    print("\n--- Sample of Generated Data ---")
    print(df.head())
    print(f"\nDataFrame shape: {df.shape}")

    # Save to CSV
    output_filename = 'simulated_transactions_v2.csv'
    df.to_csv(output_filename, index=False)
    print(f"\nData successfully saved to {output_filename}")
else:
    print("No transactions were generated. Check simulation logic.")