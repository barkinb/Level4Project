import scipy.stats as stats
import re

def parse_distribution(distribution_str):

    try:
        match = re.match(r'(\w+)\((.*?)\)', distribution_str)
        try:
            dist_type = match.group(1)
            params = [float(param) for param in match.group(2).split(',')]
            distribution_name, distribution_type = None, None
            if dist_type == 'Normal':
                distribution_name = stats.norm(*params)
                distribution_type = "cont"
            elif dist_type == 'Uniform':
                distribution_name = stats.uniform(*params)
                distribution_type = "cont"
            elif dist_type == 'Poisson':
                distribution_name = stats.poisson(*params)
                distribution_type = "discrete"
            elif dist_type == 't':
                distribution_name = stats.t(*params)
                distribution_type = "cont"
            elif dist_type == 'Exponential':
                distribution_name = stats.expon(*params)
                distribution_type = "cont"
            elif dist_type == 'Gamma':
                distribution_name = stats.gamma(*params)
                distribution_type = "cont"
            elif dist_type == 'Beta':
                distribution_name = stats.beta(*params)
                distribution_type = "cont"
            elif dist_type == 'Binomial':
                distribution_name = stats.binom(*params)
                distribution_type = "discrete"
            elif dist_type == 'Geometric':
                distribution_name = stats.geom(*params)
                distribution_type = "discrete"
            elif dist_type == 'Logistic':
                distribution_name = stats.logistic(*params)
                distribution_type = "cont"
            elif dist_type == 'NegativeBinomial':
                distribution_name = stats.nbinom(*params)
                distribution_type = "discrete"
            elif dist_type == 'UniformDiscrete':
                distribution_name = stats.randint(*params)
                distribution_type = "discrete"
            print(distribution_name)
            return distribution_name, distribution_type
        except Exception as e:
            print(f"Error parsing distribution_name: {e}")

    except Exception as e:
        print(f"Error parsing distribution_name: {e}")
