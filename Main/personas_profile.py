import numpy as np

# Helper to create a probability "peak"
def create_hourly_prob(peak_hour, std_dev, max_prob):
    """Creates a 24-hr list of probabilities centered around a peak_hour."""
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
            'prob_weekday': create_hourly_prob(peak_hour=12.5, std_dev=0.5, max_prob=0.95),
            'prob_weekend': create_hourly_prob(peak_hour=13, std_dev=3, max_prob=0.2),
            'amount_mean': 12.00,
            'amount_std': 2.00
        },
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=1, max_prob=0.1),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=2, max_prob=0.6), # High prob on weekend
            'amount_mean': 120.00,
            'amount_std': 35.00
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
            'prob_weekday': create_hourly_prob(peak_hour=22, std_dev=1.5, max_prob=0.7), # Late night peak
            'prob_weekend': create_hourly_prob(peak_hour=23, std_dev=1.5, max_prob=0.8),
            'amount_mean': 25.00,
            'amount_std': 5.00
        },
        'groceries': {
            'prob_weekday': create_hourly_prob(peak_hour=18, std_dev=1, max_prob=0.1),
            'prob_weekend': create_hourly_prob(peak_hour=14, std_dev=2, max_prob=0.6), # High prob on weekend
            'amount_mean': 25.00,
            'amount_std': 10.00
        }
    }
}