"""
A Simulated annealing framework for inverse
:copyright:
    ZIYI XI(xiziyi2015@gmail.com)
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

from mpi4py import MPI
# import multiprocessing as mp
import numpy as np
import sys
import configparser
import os
import wrap

def SA(functionName='test'):
    cf=configparser.ConfigParser()
    cf.read('./config.ini')
    CpuNumber=cf.getint('system','CpuNumber')
    ParameterNumber=cf.getint('model','ParameterNumber')

    comm = MPI.COMM_SELF.Spawn('python',args=[os.path.dirname(os.path.abspath(__file__))+'/main.py'],maxprocs=CpuNumber)
    
    pool=wrap.PoolMatlab(CpuNumber,functionName)

    positionContainer=np.zeros((CpuNumber,ParameterNumber))

    comm.Gather(None,positionContainer,root=MPI.ROOT)
    comm.Scatter(np.array(pool.map(positionContainer)),None,root=MPI.ROOT) 

    R=int(comm.recv(source=0,tag=0))
    for i in range(R):
        comm.Gather(None,positionContainer,root=MPI.ROOT)
        comm.Scatter(np.array(pool.map(positionContainer)),None,root=MPI.ROOT)

    while(R!=0):
        R=int(comm.recv(source=0,tag=0))
        if(R == 0):
            break
        for i in range(R):
            comm.Gather(None,positionContainer,root=MPI.ROOT)
            comm.Scatter(np.array(pool.map(positionContainer)),None,root=MPI.ROOT)

    energyContainer=np.zeros(CpuNumber)
    comm.Gather(None,energyContainer,root=MPI.ROOT)
    comm.Gather(None,positionContainer,root=MPI.ROOT)
    thePosition=np.argmin(energyContainer)

    return energyContainer[thePosition],positionContainer[thePosition]

    comm.Disconnect()

if(__name__=='__main__'):
    SA(functionName='Forward')