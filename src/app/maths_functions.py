import numpy as np
def ni(n,i):
    return np.math.factorial(n) / (np.math.factorial(n) * np.math.factorial(n-i))

def basis(n,i,t):
    J = np.array(ni(n,i) * (t**i) * (1-t) ** (n-i))
    return J

