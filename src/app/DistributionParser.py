import re

import scipy.stats as stats


def parse_distribution(distribution_str):
    """Returns the name, parameters, type for a probability distribution"""
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
        return e

def get_distribution_text() -> str:
    """Returns the name and parameters for a distribution"""
    return '''Enter None to remove the statistical distributions for this axis.
    Please select an Axis of your choosing and enter a probability distribution from the following:

    * Normal Distribution (scipy.stats.norm):
        * Parameters: mean (loc), standard deviation (scale)
        * Enter as: Normal(loc, scale)
    * Uniform Distribution (scipy.stats.uniform):
        * Parameters: lower boundary (loc), upper boundary (scale)
        * Enter as: Uniform(loc, scale)
    * Poisson Distribution (scipy.stats.poisson):
        * Parameter: rate (μ)
        * Enter as: Poisson(μ)
    * Student's t Distribution (scipy.stats.t):
        * Parameters: degrees of freedom (df)
        * Enter as: t(df)
    * Exponential Distribution (scipy.stats.expon):
        * Parameter: rate (scale)
        * Enter as: Exponential(scale)
    * Gamma Distribution (scipy.stats.gamma):
        * Parameters: shape (a), scale (scale)
        * Enter as: Gamma(a, scale)
    * Beta Distribution (scipy.stats.beta):
        * Parameters: shape parameter α (a), shape parameter β (b)
        * Enter as: Beta(a, b)
    * Binomial Distribution (scipy.stats.binom):
        * Parameters: number of trials (n), probability of success (p)
        * Enter as: Binomial(n, p)
    * Geometric Distribution (scipy.stats.geom):
        * Parameter: probability of success (p)
        * Enter as: Geometric(p)
    * Logistic Distribution (scipy.stats.logistic):
        * Parameters: location (loc), scale (scale)
        * Enter as: Logistic(loc, scale)
    * Negative Binomial Distribution (scipy.stats.nbinom):
        * Parameters: number of successes (r), probability of success (p)
        * Enter as: NegativeBinomial(r, p)
    * Uniform Discrete Distribution:
        * Parameters: lower boundary (a), upper boundary (b)
        * Enter as: UniformDiscrete(a, b)'''
