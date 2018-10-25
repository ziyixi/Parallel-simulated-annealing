"""
A Simulated annealing framework for inverse
:copyright:
    ZIYI XI(xiziyi2015@gmail.com)
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

from mpi4py import MPI
import multiprocessing as mp
import numpy as np
import sys
import configparser
import os

def f(parameters):
    objectFunction=gg
    parameterList=''
    for i in parameters:
        parameterList+=str(i)+','
    parameterList='objectFunction('+parameterList[:-1]+')'
    # print(eval(parameterList))
    # print(parameterList)
    value=eval(parameterList)
    return value


cf=configparser.ConfigParser()
cf.read('./config.ini')
CpuNumber=cf.getint('system','CpuNumber')
ParameterNumber=cf.getint('model','ParameterNumber')

def SA(g):
    global gg
    gg=g
    comm = MPI.COMM_SELF.Spawn('python',args=[os.path.dirname(os.path.abspath(__file__))+'/main.py'],maxprocs=CpuNumber)
    pool=mp.Pool(processes=CpuNumber)

    positionContainer=np.zeros((CpuNumber,ParameterNumber))

    comm.Gather(None,positionContainer,root=MPI.ROOT)
    comm.Scatter(np.array(pool.map(f,positionContainer)),None,root=MPI.ROOT) 

    R=int(comm.recv(source=0,tag=0))
    for i in range(R):
        comm.Gather(None,positionContainer,root=MPI.ROOT)
        comm.Scatter(np.array(pool.map(f,positionContainer)),None,root=MPI.ROOT)

    while(R!=0):
        R=int(comm.recv(source=0,tag=0))
        if(R == 0):
            break
        for i in range(R):
            comm.Gather(None,positionContainer,root=MPI.ROOT)
            comm.Scatter(np.array(pool.map(f,positionContainer)),None,root=MPI.ROOT)

    energyContainer=np.zeros(CpuNumber)
    comm.Gather(None,energyContainer,root=MPI.ROOT)
    comm.Gather(None,positionContainer,root=MPI.ROOT)
    thePosition=np.argmin(energyContainer)

    return energyContainer[thePosition],positionContainer[thePosition]

    comm.Disconnect()

if(__name__=='__main__'):
    def f(parameters):
        x1=parameters[0]
        x2=parameters[1]
        x3=parameters[2]
        x4=parameters[3]
        res=-20*np.exp(-0.2*np.sqrt(0.25*(x1*x1+x2*x2+x3*x3+x4*x4)))-np.exp(0.25*(np.cos(4*x1)+np.cos(4*x2)+np.cos(4*x3)+np.cos(4*x4)))+20+np.exp(1)
        return res
    print(SA(f))
