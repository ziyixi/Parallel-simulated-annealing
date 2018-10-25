import sys
sys.path.append("../..")
import init
import numpy as np

def f(parameters):
    x1=parameters[0]
    x2=parameters[1]
    res=100*((np.sin(x1**2-x2**2)**2-0.5)/((1+0.001*(x1**2+x2**2))**2)-0.5)
    return res

print(init.SA(f))