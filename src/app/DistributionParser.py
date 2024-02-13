import scipy.stats as stats
import re

def parse_distribution(distribution_str):
    try:
        match = re.match(r'(\w+)\((.*?)\)', distribution_str)
        if match:
            dist_type = match.group(1)
            params = [float(param) for param in match.group(2).split(',')]

            if dist_type == 'Normal':
                distribution = stats.norm(*params)
            elif dist_type == 'Uniform':
                distribution = stats.uniform(*params)
            elif dist_type == 'Poisson':
                distribution = stats.poisson(*params)
            elif dist_type == 't':
                distribution = stats.t(*params)
            elif dist_type == 'Exponential':
                distribution = stats.expon(*params)
            elif dist_type == 'Gamma':
                distribution = stats.gamma(*params)
            elif dist_type == 'Beta':
                distribution = stats.beta(*params)
            elif dist_type == 'Binomial':
                distribution = stats.binom(*params)
            elif dist_type == 'Geometric':
                distribution = stats.geom(*params)
            elif dist_type == 'Hypergeometric':
                distribution = stats.hypergeom(*params)
            elif dist_type == 'Logistic':
                distribution = stats.logistic(*params)
            elif dist_type == 'Lognormal':
                distribution = stats.lognorm(*params)
            elif dist_type == 'NegativeBinomial':
                distribution = stats.nbinom(*params)
            elif dist_type == 'UniformDiscrete':
                distribution = stats.randint(*params)
            elif dist_type == 'Wald':
                distribution = stats.wald(*params)
            elif dist_type == 'Weibull':
                distribution = stats.weibull_min(*params)
            else:
                raise ValueError('Distribution could not be parsed correctly')
            print(distribution)
            return distribution
    except Exception as e:
        print(f"Error parsing distribution: {e}")
