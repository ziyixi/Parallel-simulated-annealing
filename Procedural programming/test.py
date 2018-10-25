"""
A Simulated annealing framework for inverse
:copyright:
    ZIYI XI(xiziyi2015@gmail.com)
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

from mpi4py import MPI
import numpy as np 
import config
import core
import sys
import random
import logging
import time
logging.basicConfig(filename=config.logFileName, level=logging.INFO)


TotalNumberCount=0 #for the use of count iteration number
comm = MPI.COMM_WORLD 
rank = comm.Get_rank()
size = comm.Get_size()
MyQueue=core.ItemStore(config.ItemStoreSize) #for the use of calculating acceptance rate
myStopQueue=core.stopQueue() #for the use of estimating if should stop

position=core.RandomInit() #the initial positions
T=config.T #the initial temprature
energy=core.f(position) #the initial energy
p=0.44 #the initial acceptance rate
theta=config.theta #the initial theta
R=config.R #the initial R

if(rank==0):
    StartTime = time.asctime( time.localtime(time.time()) )
    logging.info('cpu numbers:'+str(config.CpuNumber))
    logging.info('command name:'+config.CommandName)
    logging.info('parameter numbers:'+str(config.ParameterNumber))
    for i,j in zip(config.RangeLow,config.RangeHigh):
        logging.info('range: '+str(i)+'~'+str(j))
    logging.info('start time at:'+StartTime)    

for i in range(config.InitLoopTime):
    #initial interation without temprature drops
    _,position,energy,theta,flag=core.Step(T,position,energy,p,theta,core.f,config.sensity,0)

    #recalculate acceptance rate to adjust moving step
    if(MyQueue.flag()):
        p=MyQueue.getP()
    MyQueue.add(flag)

    #TODO remove it
    # print('rank: ',rank,'T: ',T,'position: ',position,'energy: ',energy,'theta',theta,'p',p,'flag',flag)
    # sys.stdout.flush()


def ALoop(R,T,position,energy,p,theta,MyQueue):
    '''
    the process between core exchanges
    input:
    R: exchange interval
    T: temprature after last exchange
    position: position after last exchange
    p: acceptance rate after last exchange
    theta: theta after last exchange
    MyQueue: the queue recording the acceptance rate
    '''
    #stopqueue refresh
    myStopQueue.refresh()

    #the normal step between exchanges
    for i in range(R):
        T,position,energy,theta,flag=core.Step(T,position,energy,p,theta,core.f,config.sensity,1)
        myStopQueue.valueadd(position)
        if(MyQueue.flag()):
            p=MyQueue.getP()

        MyQueue.add(flag)
        #TODO remove it
        # print('rank:',rank,'T:',T,'position:',position,'energy:',energy,'theta:',theta,'R:',R,'flag:',flag,'p',p)
        # sys.stdout.flush()

    #MPI allgather, EnergyStatus records all core's energy information, StopStatus records any core wanting to stop
    EnergyStatus=np.array(comm.allgather(energy))
    EnergyStatus=config.energyC*(EnergyStatus-np.min(EnergyStatus))
    StopStatus=np.array(comm.allgather(myStopQueue.isstop()))
    # print(rank,'flag 1')
    # sys.stdout.flush()
    comm.barrier()

    #if any core wants to stop, then do it
    if(np.any(StopStatus)):
        return(T,position,energy,theta,R,0,MyQueue)
    # print(rank,'flag 2')
    # sys.stdout.flush()
    #the possibility every core jump to the condition of other core    
    JumpPossibility=np.exp(-1*EnergyStatus/T)/np.sum(np.exp(-1*EnergyStatus/T))
    RandomNumber=random.random()
    JumpPossibilitySum=np.array([np.sum(JumpPossibility[:i+1]) for i in range(config.CpuNumber)])
    flag=0
    # print(rank,'flag 3')
    # sys.stdout.flush()
    for i,value in enumerate(JumpPossibilitySum):
        if(value>=RandomNumber):
            break
        else:
            flag=i+1

    comm.barrier()
    
    #the possibility
    NewPositionInformation=np.array(comm.allgather(flag))
    # print(rank,'flag 4')
    # sys.stdout.flush()
    #adjust R according to the condition of exchange
    countDic={}
    for i in NewPositionInformation:
        countDic[i]=0
    aR=len(countDic)/config.CpuNumber
    R=int(R*np.exp(2*np.log(2)*(aR-0.5)))+1
    
    #MPI send all the information between two cores related to exchange, the tag is specially numbered
    SendCount=0
    # print(rank,'flag 5',NewPositionInformation,JumpPossibility,JumpPossibilitySum)
    # sys.stdout.flush()
    TagTemp=10**(len(str(config.CpuNumber))) 
    for i,value in enumerate(NewPositionInformation):
        if(value==rank and i!=rank):

            comm.isend(position, dest=int(i), tag=1*(TagTemp**2)+i*TagTemp+rank)
            comm.isend(energy, dest=int(i), tag=2*(TagTemp**2)+i*TagTemp+rank)
            comm.isend(theta, dest=int(i), tag=3*(TagTemp**2)+i*TagTemp+rank)
            comm.isend(MyQueue,dest=int(i), tag=4*(TagTemp**2)+i*TagTemp+rank)

    if(flag!=rank):

        position=comm.recv(source=int(flag), tag=1*(TagTemp**2)+rank*TagTemp+flag)
        energy=comm.recv(source=int(flag), tag=2*(TagTemp**2)+rank*TagTemp+flag)
        theta=comm.recv(source=int(flag), tag=3*(TagTemp**2)+rank*TagTemp+flag)
        MyQueue=comm.recv(source=int(flag), tag=4*(TagTemp**2)+rank*TagTemp+flag)
    # print(rank,'flag 6')
    # sys.stdout.flush()

    comm.barrier()
    return(T,position,energy,theta,R,1,MyQueue)

if(rank == 0):
    StartDropTime=time.asctime( time.localtime(time.time()) )
    logging.info('temprature start drop at:'+StartDropTime)

#The main function, MainFlag represents iterating or not
MainFlag=1
while(MainFlag==1 and T>10e-8):
    TotalNumberCount+=R
    T,position,energy,theta,R,MainFlag,MyQueue=ALoop(R,T,position,energy,p,theta,MyQueue)

#TODO convert to a readable form or a log file
# print(rank,'finalposition',position)
# sys.stdout.flush()
# print(rank,'finalenergy',energy)
# sys.stdout.flush()
# print(rank,'numbercount',TotalNumberCount)
# sys.stdout.flush()

finalPositionInformation=comm.allgather(position)
finalEnergyInformation=comm.allgather(energy)
if(rank == 0):
    EndTime=time.asctime( time.localtime(time.time()) )
    logging.info('program stop at:'+EndTime)
    logging.info('accuracy:'+','.join(str(x) for x in config.stopMoveStep))
    for i,j,k in zip(range(config.CpuNumber),finalPositionInformation,finalEnergyInformation):
        logging.info('core order:'+str(i))
        logging.info('final position:'+','.join(str(x) for x in j))
        logging.info('final energy: '+str(k))
        # logging.info('\n')