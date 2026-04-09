import numpy as np

# Helper to create a probability "peak"
def create_hourly_prob(peak_hour, std_dev, max_prob):
    """
    Creates a 24-hr list of probabilities centered around a peak_hour.
    """
    hours = np.arange(24)
    # Use a Gaussian (normal distribution) to create a smooth curve
    prob = np.exp(-((hours - peak_hour)**2) / (2 * std_dev**2)) 
    # Normalize and scale to the max probability
    prob = (prob / np.max(prob)) * max_prob
    return prob.tolist()

# Persona 1: Commuter Profile
COMMUTER_PROFILE = {
    'user_id_prefix': 'USER_COMMUTER_',
    'categories': {
        'coffee': {
            'prob_weekday': create_hourly_prob(peak_hour=8, std_dev=1, max_prob=0.9),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.3),
            'amount_mean': 4.50,
            'amount_std': 0.50
        },
        'lunch': {
            'prob_weekday': create_hourly_prob(peak_hour=12.5, std_dev=1, max_prob=0.75),
            'prob_weekend': create_hourly_prob(peak_hour=13, std_dev=3, max_prob=0.2),
            'amount_mean': 12.00,
            'amount_std': 2.00
        },
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=1, max_prob=0.1),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=2, max_prob=0.6), # High prob on weekend
            'amount_mean': 120.00,
            'amount_std': 35.00
        },
        'subscription': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 10.99,
            'amount_std': 2.00
        },
        'phone_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 28.00,
            'amount_std': 6.00
        },
        'utility_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 85.00,
            'amount_std': 20.00
        },
        'transport_public': {
            'prob_weekday': (
                np.array(create_hourly_prob(peak_hour=8, std_dev=0.8, max_prob=0.75)) +
                np.array(create_hourly_prob(peak_hour=18, std_dev=0.9, max_prob=0.55))
            ).clip(0, 0.95).tolist(),
            'prob_weekend': create_hourly_prob(peak_hour=13, std_dev=3, max_prob=0.15),
            'amount_mean': 2.80,
            'amount_std': 1.20
        },
        'transport_ride_hail': {
            'prob_weekday': create_hourly_prob(peak_hour=23, std_dev=1.8, max_prob=0.05),
            'prob_weekend': create_hourly_prob(peak_hour=1, std_dev=2.0, max_prob=0.10),
            'amount_mean': 14.00,
            'amount_std': 6.00
        }
    }
}

# Persona 2: Student Profile
STUDENT_PROFILE = {
    'user_id_prefix': 'USER_STUDENT_',
    'categories': {
        'coffee': {
            'prob_weekday': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.5), # Later start
            'prob_weekend': create_hourly_prob(peak_hour=13, std_dev=3, max_prob=0.4),
            'amount_mean': 3.50,
            'amount_std': 0.50
        },
        'food_delivery': {
            'prob_weekday': create_hourly_prob(peak_hour=22, std_dev=1.5, max_prob=0.35), # Late night peak
            'prob_weekend': create_hourly_prob(peak_hour=23, std_dev=1.5, max_prob=0.25),
            'amount_mean': 25.00,
            'amount_std': 5.00
        },
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=1, max_prob=0.1),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=2, max_prob=0.6), # High prob on weekend
            'amount_mean': 25.00,
            'amount_std': 10.00
        },
        'subscription': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 7.99,
            'amount_std': 1.50
        },
        'phone_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 18.00,
            'amount_std': 5.00
        },
        'utility_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 55.00,
            'amount_std': 15.00
        },
        'transport_public': {
            'prob_weekday': create_hourly_prob(peak_hour=10, std_dev=2.0, max_prob=0.25),
            'prob_weekend': create_hourly_prob(peak_hour=15, std_dev=3.0, max_prob=0.30),
            'amount_mean': 2.20,
            'amount_std': 1.00
        },
        'transport_ride_hail': {
            'prob_weekday': create_hourly_prob(peak_hour=0.5, std_dev=2.2, max_prob=0.08),
            'prob_weekend': create_hourly_prob(peak_hour=1.5, std_dev=2.2, max_prob=0.14),
            'amount_mean': 11.00,
            'amount_std': 5.00
        }
    }
}

# Persona 3: Homebody Profile
HOMEBODY_PROFILE = {
    'user_id_prefix': 'USER_HOME_',
    'categories': {
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=16, std_dev=2, max_prob=0.08),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=2, max_prob=0.35),
            'amount_mean': 55.00,
            'amount_std': 20.00
        },
        'online_shopping': {
            'prob_weekday': create_hourly_prob(peak_hour=20, std_dev=3, max_prob=0.06),
            'prob_weekend': create_hourly_prob(peak_hour=21, std_dev=3, max_prob=0.08),
            'amount_mean': 35.00,
            'amount_std': 25.00
        },
        'coffee': {
            'prob_weekday': create_hourly_prob(peak_hour=10, std_dev=2, max_prob=0.08),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.10),
            'amount_mean': 3.80,
            'amount_std': 0.60
        },
        'food_delivery': {
            'prob_weekday': create_hourly_prob(peak_hour=19.5, std_dev=2.5, max_prob=0.08),
            'prob_weekend': create_hourly_prob(peak_hour=20.5, std_dev=2.5, max_prob=0.12),
            'amount_mean': 22.00,
            'amount_std': 7.00
        },

        # recurring categories (set to zero probs; injected by your recurring scheduler)
        'subscription': {'prob_weekday': [0.0]*24, 'prob_weekend': [0.0]*24, 'amount_mean': 9.99, 'amount_std': 2.0},
        'phone_bill':   {'prob_weekday': [0.0]*24, 'prob_weekend': [0.0]*24, 'amount_mean': 20.00, 'amount_std': 5.0},
        'utility_bill': {'prob_weekday': [0.0]*24, 'prob_weekend': [0.0]*24, 'amount_mean': 70.00, 'amount_std': 18.0},
    }
}

# Persona 4: Professional Profile
PROFESSIONAL_PROFILE = {
    'user_id_prefix': 'USER_PROFESSIONAL_',
    'categories': {
        'coffee': {
            'prob_weekday': create_hourly_prob(peak_hour=8, std_dev=1, max_prob=0.85),
            'prob_weekend': create_hourly_prob(peak_hour=10, std_dev=2, max_prob=0.5),
            'amount_mean': 6.00,
            'amount_std': 1.00
        },
        'dining_out': {
            'prob_weekday': create_hourly_prob(peak_hour=13, std_dev=1, max_prob=0.4),
            'prob_weekend': create_hourly_prob(peak_hour=19, std_dev=2, max_prob=0.6),
            'amount_mean': 35.00,
            'amount_std': 15.00
        },
        'foreign_dining': {
            'prob_weekday': create_hourly_prob(peak_hour=19, std_dev=2, max_prob=0.04),
            'prob_weekend': create_hourly_prob(peak_hour=20, std_dev=2, max_prob=0.06),
            'amount_mean': 45.00,
            'amount_std': 20.00
        },
        'transport_ride_hail': {
            'prob_weekday': create_hourly_prob(peak_hour=8.5, std_dev=1, max_prob=0.15),
            'prob_weekend': create_hourly_prob(peak_hour=23, std_dev=2, max_prob=0.3),
            'amount_mean': 22.00,
            'amount_std': 8.00
        },
        'online_shopping': {
            'prob_weekday': create_hourly_prob(peak_hour=21, std_dev=2, max_prob=0.1),
            'prob_weekend': create_hourly_prob(peak_hour=20, std_dev=3, max_prob=0.15),
            'amount_mean': 85.00,
            'amount_std': 40.00
        },
        'gym': {
            'prob_weekday': create_hourly_prob(peak_hour=7, std_dev=1, max_prob=0.15),
            'prob_weekend': create_hourly_prob(peak_hour=9, std_dev=1.5, max_prob=0.4),
            'amount_mean': 60.00,
            'amount_std': 10.00
        },
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=1, max_prob=0.08),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.4),
            'amount_mean': 90.00,
            'amount_std': 30.00
        },
        'subscription': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 14.99,
            'amount_std': 3.00
        },
        'phone_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 55.00,
            'amount_std': 10.00
        },
        'utility_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 130.00,
            'amount_std': 25.00
        },
    }
}

# Persona 5: Retiree Profile
RETIREE_PROFILE = {
    'user_id_prefix': 'USER_RETIREE_',
    'categories': {
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=10, std_dev=2, max_prob=0.15),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.2),
            'amount_mean': 65.00,
            'amount_std': 20.00
        },
        'pharmacy': {
            'prob_weekday': create_hourly_prob(peak_hour=10, std_dev=2, max_prob=0.15),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.05),
            'amount_mean': 18.00,
            'amount_std': 8.00
        },
        'coffee': {
            'prob_weekday': create_hourly_prob(peak_hour=10, std_dev=2, max_prob=0.06),
            'prob_weekend': create_hourly_prob(peak_hour=11, std_dev=2, max_prob=0.08),
            'amount_mean': 3.50,
            'amount_std': 0.50
        },
        'online_shopping': {
            'prob_weekday': create_hourly_prob(peak_hour=14, std_dev=3, max_prob=0.03),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=3, max_prob=0.03),
            'amount_mean': 25.00,
            'amount_std': 15.00
        },
        'food_delivery': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=2, max_prob=0.04),
            'prob_weekend': create_hourly_prob(peak_hour=18, std_dev=2, max_prob=0.05),
            'amount_mean': 18.00,
            'amount_std': 5.00
        },
        'subscription': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 5.99,
            'amount_std': 1.00
        },
        'phone_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 15.00,
            'amount_std': 3.00
        },
        'utility_bill': {
            'prob_weekday': [0.0]*24,
            'prob_weekend': [0.0]*24,
            'amount_mean': 95.00,
            'amount_std': 20.00
        },
    }
}