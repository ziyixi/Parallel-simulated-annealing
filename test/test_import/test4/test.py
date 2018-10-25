import sys
sys.path.append("../..")
import init
import numpy as np

def f(parameters):
    x1=parameters[0]
    x2=parameters[1]
    res=-20*np.exp(-0.2*np.sqrt(0.5*(x1*x1+x2*x2)))-np.exp(0.5*(np.cos(4*x1)+np.cos(4*x2)))+20+np.exp(1)
    return res

print(init.SA(f))