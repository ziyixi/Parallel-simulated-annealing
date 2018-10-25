import sys
sys.path.append("..")
import init
import numpy as np
from ctypes import *

#ctype decoration
f=cdll.LoadLibrary('./test.so').dog
f.argtypes=[c_double,c_double,c_double,c_double]
f.restype=c_double
# print(init.SA(f))
init.SA(f)