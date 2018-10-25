import sys
sys.path.append("../..")
import init
import numpy as np
from numba import jit

@jit(nopython=True)
def f(x1,x2,x3,x4):
    res=-20*np.exp(-0.2*np.sqrt(0.25*(x1*x1+x2*x2+x3*x3+x4*x4)))-np.exp(0.25*(np.cos(4*x1)+np.cos(4*x2)+np.cos(4*x3)+np.cos(4*x4)))+20+np.exp(1)
    return res

print(init.SA(f))