"""
A parallel simulated annealing framework for inverse
:copyright:
    ZIYI XI(xiziyi2015@gmail.com)
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

import numpy as np
from numpy import inf
import configparser

cf=configparser.ConfigParser()
cf.read('./config.ini')

#algorithms
# TLambda=0.001
TLambda=cf.getfloat('algorithms','TLambda')

# K=1
K=cf.getfloat('algorithms','K')

# C=1
C=cf.getfloat('algorithms','C')

# T=500
T=cf.getfloat('algorithms','T')

# R=300
R=cf.getint('algorithms','R')

InitLoopTime=cf.getint('algorithms','InitLoopTime')
# InitLoopTime=3000

ItemStoreSize=cf.getint('algorithms','ItemStoreSize')
# ItemStoreSize=10

#system
# CpuNumber=8
CpuNumber=cf.getint('system','CpuNumber')

#model
# ParameterNumber=6
ParameterNumber=cf.getint('model','ParameterNumber')

RangeHigh=np.zeros(ParameterNumber)
RangeHigh=cf.get('model','RangeHigh').split(',')
for i,value in enumerate(RangeHigh):
    try:
        RangeHigh[i]=float(value)
    except:
        RangeHigh[i]=np.inf

RangeLow=np.zeros(ParameterNumber)
RangeLow=cf.get('model','RangeLow').split(',')
for i,value in enumerate(RangeLow):
    try:
        RangeLow[i]=float(value)
    except:
        RangeLow[i]=-np.inf

# setrange=1
setrange=cf.getfloat('model','setrange')

# CommandName='./a'
CommandName=cf.get('model','CommandName')

# sensity=np.array([0.000001,0.000001,0.000001,0.000001,0.000001,0.000001])
sensity=np.array([float(i) for i in cf.get('model','sensity').split(',')])

# stopMoveStep=np.array([0.0000001,0.0000001,0.0000001,0.000001,0.000001,0.000001])
stopMoveStep=np.array([float(i) for i in cf.get('model','stopMoveStep').split(',')])

# stopRepeateTimes=30
stopRepeateTimes=cf.getint('model','stopRepeateTimes')

# theta=0.0001
theta=cf.getfloat('model','theta')

energyC=cf.getfloat('model','energyC')
logFileName=cf.get('model','logFileName')