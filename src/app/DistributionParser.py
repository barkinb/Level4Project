import scipy.stats as stats
import re
from tkinter import messagebox

def parse_distribution(distribution_str):
    try:
        match = re.match(r'(\w+)\((.*?)\)', distribution_str)

        dist_type = match.group(1).title()
        params = [float(param) for param in match.group(2).split(',')]
        distribution_functions = {
            'Normal': {'function': stats.norm, 'type': 'continuous', 'params': params},
            'Uniform': {'function': stats.uniform, 'type': 'continuous', 'params': params},
            'Poisson': {'function': stats.poisson, 'type': 'discrete', 'params': params},
            't': {'function': stats.t, 'type': 'continuous', 'params': params},
            'Exponential': {'function': stats.expon, 'type': 'continuous', 'params': params},
            'Gamma': {'function': stats.gamma, 'type': 'continuous', 'params': params},
            'Beta': {'function': stats.beta, 'type': 'continuous', 'params': params},
            'Binomial': {'function': stats.binom, 'type': 'discrete', 'params': params},
            'Geometric': {'function': stats.geom, 'type': 'discrete', 'params': params},
            'Logistic': {'function': stats.logistic, 'type': 'continuous', 'params': params},
            'NegativeBinomial': {'function': stats.nbinom, 'type': 'discrete', 'params': params},
            'UniformDiscrete': {'function': stats.randint, 'type': 'discrete', 'params': params}
        }

        return distribution_functions[dist_type]

    except Exception as e:
        messagebox.showerror("Error",f"Error parsing distribution_name: {e}")

