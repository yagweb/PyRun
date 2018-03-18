import numpy as np
from scipy import interpolate

def test_scipy():
    
    x = np.arange(0, 10)
    y = np.exp(-x/3.0)
    f = interpolate.interp1d(x, y)
    xnew = np.arange(0, 9, 0.1)
    ynew = f(xnew)
    print(ynew)
    
test_scipy()