import sys
sys.path.append("../..")
import init
import numpy as np

def f(parameters):
    x1=parameters[0]
    x2=parameters[1]
    res=20+x1**2+x2**2-10*(np.cos(2*np.pi*x1)+np.cos(2*np.pi*x2))
    return res

print(init.SA(f))