
import scipy.stats as stats
import re


def parse_distribution(distribution_str):
    try:
        match = re.match(r'(\w+)\((.*?)\)', distribution_str)
        if match:
            dist_type = match.group(1)
            params = [float(param) for param in match.group(2).split(',')]

            if dist_type == 'Normal':
                return stats.norm(*params)
            elif dist_type == 'Uniform':
                return stats.uniform(*params)
            elif dist_type == 'Poisson':
                return stats.poisson(*params)
            elif dist_type == 't':
                return stats.t(*params)

            else:
                raise ValueError('Distribution could not be parsed correctly')
            
    except Exception as e:
        print(f"Error parsing distribution: {e}")


