import scipy.stats as stats
import re
from tkinter import messagebox

def parse_distribution(distribution_str):
    try:
        match = re.match(r'(\w+)\((.*?)\)', distribution_str)

        dist_type = match.group(1).title()
        params = [float(param) for param in match.group(2).split(',')]
        distribution_functions = {
            'Normal': {'function': stats.norm, 'type': 'continuous'},
            'Uniform': {'function': stats.uniform, 'type': 'continuous'},
            'Poisson': {'function': stats.poisson, 'type': 'discrete'},
            't': {'function': stats.t, 'type': 'continuous'},
            'Exponential': {'function': stats.expon, 'type': 'continuous'},
            'Gamma': {'function': stats.gamma, 'type': 'continuous'},
            'Beta': {'function': stats.beta, 'type': 'continuous'},
            'Binomial': {'function': stats.binom, 'type': 'discrete'},
            'Geometric': {'function': stats.geom, 'type': 'discrete'},
            'Logistic': {'function': stats.logistic, 'type': 'continuous'},
            'NegativeBinomial': {'function': stats.nbinom, 'type': 'discrete'},
            'UniformDiscrete': {'function': stats.randint, 'type': 'discrete'}
        }
        distribution_functions[dist_type]['params'] = params
        return distribution_functions[dist_type]

    except Exception as e:
        messagebox.showerror("Error",f"Error parsing distribution_name: {e}")

