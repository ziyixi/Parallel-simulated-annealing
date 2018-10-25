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
import sys
import random
import logging
import time
from numpy import inf
import configparser
import random
import subprocess


class ItemStore(object):
    '''
    A queue which pops the first item when it's full
    values:
    items: the queue
    Mycount: a cursor for further use
    maxsize: the size of the queue
    
    functions:
    add: add a value
    getAll: get all the value
    getP: get the acceptance rate when the queue using for the purpose of calculating acceptance rate
    flag: every maxsize step, the queue could recalculate acceptance rate
    isFinal: if no move (all the value equals to 2, then stop the program)
    '''
    def __init__(self,maxsize=0):
        self.items=np.zeros(maxsize)
        self.MyCount=0
        self.maxsize=maxsize
        if(self.maxsize!=0):
            self.MAX=False
        else:
            self.MAX=True
    def add(self,item):
        if(self.MyCount>=self.maxsize):
            self.MyCount=0
            self.MAX=True
        self.items[self.MyCount]=item
        self.MyCount+=1
    def getAll(self):
        return self.items
    def getP(self):
        temp=0
        for i in self.items:
            if(i==0 or i==1):
                temp+=1
        return temp/self.maxsize
    def flag(self):
        if(self.MyCount==self.maxsize):
            return True
        else:
            return False
    def isFinal(self):
        if(np.all(self.items==2)):
            return True
        else:
            return False

class stopQueue(object):
    '''
    If stopcount is equal to stopRepeateTimes, the program will abort
    '''
    def __init__(self,ParameterNumber,stopRepeateTimes,stopMoveStep):
        self.ParameterNumber=ParameterNumber
        self.stopRepeateTimes=stopRepeateTimes
        self.stopMoveStep=stopMoveStep

        self.stopCount=0
        self.lasttimevalue=np.zeros(self.ParameterNumber)
    def isstop(self):
        if(self.stopCount>self.stopRepeateTimes):
            return True
        else:
            return False
    def valueadd(self,thistimevalue):
        if(np.all(thistimevalue-self.lasttimevalue<=self.stopMoveStep)):
            self.stopCount+=1
        else:
            self.stopCount=0
        self.lasttimevalue=thistimevalue
    def refresh(self):
        self.stopCount=0
        self.lasttimevalue=np.zeros(self.ParameterNumber)

class SA(object):
    def __init__(self,logFileName='log'):
        self.TLambda=0.001
        self.K=1
        self.C=1
        self.T=50000
        self.R=300
        self.InitLoopTime=3000
        self.ItemStoreSize=10
        self.CpuNumber=8
        self.ParameterNumber=6
        self.RangeHigh=np.zeros(self.ParameterNumber)
        self.RangeLow=np.zeros(self.ParameterNumber)
        self.setrange=1
        self.CommandName='./a'
        self.sensity=np.array([1,1,1,1,1,1])
        self.stopMoveStep=np.array([0.001,0.001,0.001,0.001,0.001,0.001])
        self.stopRepeateTimes=30
        self.theta=0.0001
        self.energyC=1
        self.logFileName=logFileName

        self.useBash=True
        # self.objectFunction=None
        self.numCount=0

    def configParse(self,configFileName='./config.ini'):
        cf=configparser.ConfigParser()
        cf.read(configFileName)
        #algorithms
        # TLambda=0.001
        self.TLambda=cf.getfloat('algorithms','TLambda')
        # K=1
        self.K=cf.getfloat('algorithms','K')
        # C=1
        self.C=cf.getfloat('algorithms','C')
        # T=500
        self.T=cf.getfloat('algorithms','T')
        # R=300
        self.R=cf.getint('algorithms','R')
        self.InitLoopTime=cf.getint('algorithms','InitLoopTime')
        # InitLoopTime=3000
        self.ItemStoreSize=cf.getint('algorithms','ItemStoreSize')
        # ItemStoreSize=10
        #system
        # CpuNumber=8
        self.CpuNumber=cf.getint('system','CpuNumber')
        #model
        # ParameterNumber=6
        self.ParameterNumber=cf.getint('model','ParameterNumber')
        self.RangeHigh=cf.get('model','RangeHigh').split(',')
        for i,value in enumerate(self.RangeHigh):
            try:
                self.RangeHigh[i]=float(value)
            except:
                self.RangeHigh[i]=np.inf
        self.RangeLow=cf.get('model','RangeLow').split(',')
        for i,value in enumerate(self.RangeLow):
            try:
                self.RangeLow[i]=float(value)
            except:
                self.RangeLow[i]=-np.inf
        # setrange=1
        self.setrange=cf.getfloat('model','setrange')
        # CommandName='./a'
        self.CommandName=cf.get('model','CommandName')
        # sensity=np.array([0.000001,0.000001,0.000001,0.000001,0.000001,0.000001])
        self.sensity=np.array([float(i) for i in cf.get('model','sensity').split(',')])
        # stopMoveStep=np.array([0.0000001,0.0000001,0.0000001,0.000001,0.000001,0.000001])
        self.stopMoveStep=np.array([float(i) for i in cf.get('model','stopMoveStep').split(',')])
        # stopRepeateTimes=30
        self.stopRepeateTimes=cf.getint('model','stopRepeateTimes')
        # theta=0.0001
        self.theta=cf.getfloat('model','theta')
        self.energyC=cf.getfloat('model','energyC')
        self.logFileName=cf.get('model','logFileName')

    def RandomInit(self):
        '''
        an evenly distrution of [RangeLow,RangeHigh] 
        input: None

        output:
        ParameterNumber numbers from an evenly distrution of [RangeLow,RangeHigh] 
        '''
        result=np.zeros(self.ParameterNumber)
        for i in range(self.ParameterNumber):
            result[i]=(random.random()-0.5)*(self.RangeHigh[i]-self.RangeLow[i])+(self.RangeHigh[i]+self.RangeLow[i])/2
        for i,value in enumerate(result):
            if(value==np.inf or value==-1*np.inf):
                result[i]=(random.random()-0.5)*self.setrange

        if(rank == 0):
            print('dd',result)
            print(self.RangeHigh[0],self.RangeLow[0],(random.random()-0.5)*(self.RangeHigh[0]-self.RangeLow[0])+(self.RangeHigh[0]+self.RangeLow[0])/2)
            print(self.RangeLow)
            sys.stdout.flush()

        return result

    def Raw_function(self,parameters,command=''):
        '''
        A raw wrap of forward program, further wrapped by f 
        input: 
        parameters: input parameters for the forward model
        command: the command name from config

        output: the output of the forward model
        '''
        temp='echo \''
        for i in parameters:
            temp+=' '+str(i)
        command=temp+'\' | '+command
        out=subprocess.check_output(command,shell=True)
        out=float(out.decode('utf-8'))
        return out

    def f(self,parameters):
        '''
        The wrapper of the forward model
        input: parameters
        output: output value
        '''
        result=self.Raw_function(parameters,command=self.CommandName)
        return result

    def setObjectFunction(self):
        self.useBash=False
        
    def objectFunction(self,parameters):
        # TagTemp=10**(len(str(self.CpuNumber))) 
        # print('flag 1',parameters,rank)
        # sys.stdout.flush()
        value=np.zeros(1)  
        commMaster.Gather(parameters,None,root=0)
        commMaster.Scatter(None,value,root=0)
        self.numCount+=1
        # print(rank,self.numCount)
        # sys.stdout.flush()
        # commMaster.Barrier()
        # print('flag 2')
        # sys.stdout.flush()    
        # print(rank,'flag 1')
        # sys.stdout.flush()
        # value=commMaster.recv(source=0,tag=rank)
        # print(rank,value)
        # sys.stdout.flush()
        return value[0]
    
    def Step(self,initFlag):
        '''
        Main function for the iteration 
        input: 
        T: temprature last time [a positive value] 
        position: position last time [numpy array with ParameterNumber value] 
        energy: energy last time [a value] 
        p: acceptance rate at the moment [a value with range from 0 to 1] 
        theta: theta that controls moving step last time [a positive value] 
        f: the function having wrapped for the forward model [a function object] 
        sensity: sensity [defined as config] 
        initFlag: if 0, then T remains constant, or T will drop  
        output: 
        T: temprature this time [a positive value] 
        position: position this time [numpy array with ParameterNumber value] 
        energy: energy this time [a value] 
        theta: theta that controls moving step this time [a positive value] 
        flag: if 0, return to a lower energy; if 1, return to a higher energy; if 2, remain in the origin position 
        '''
        # self.numCount+=1
        #control temprature
        OutOfRange=False
        if(initFlag==0):
            self.T=self.T
        else:
            self.T=(1-self.TLambda)*self.T
        
        #renew data 
        thetaNew=self.theta*np.exp(self.K*(self.p-0.44))
        deltaX=self.C*np.random.laplace(0,thetaNew,self.ParameterNumber)*self.sensity
        #moving
        positionNew=self.position+deltaX
        #boundary check
        for i,value in enumerate(positionNew):
            if(value<self.RangeLow[i]):
                self.theta=self.theta/1.93
                OutOfRange=True
                positionNew=self.position
            if(value>self.RangeHigh[i]):
                self.theta=self.theta/1.93
                OutOfRange=True
                positionNew=self.position
        # print(rank,'flag')
        # sys.stdout.flush()
        if(self.useBash):    
            energyNew=self.f(positionNew)
        else:
            energyNew=self.objectFunction(positionNew)
        #jump status

        if(OutOfRange):
            return(2)

        if(energyNew<self.energy):
            self.position=positionNew
            self.energy=energyNew
            self.theta=thetaNew
            return(0)
        else:
            possibility=np.exp(-(energyNew-self.energy)/self.T)
            if(possibility>random.random()):
                self.position=positionNew
                self.energy=energyNew
                self.theta=thetaNew
                return(1)
            else:
                self.theta=thetaNew
                return(2)
    
    def ALoop(self):
        '''
        the process between core exchanges
        '''
        #stopqueue refresh
        self.myStopQueue.refresh()
        # print(rank,self.R)
        # sys.stdout.flush()
        if(rank==0):
            commMaster.send(self.R,dest=0,tag=0)
        #the normal step between exchanges
        for i in range(self.R):
            flag=self.Step(1)
            self.myStopQueue.valueadd(self.position)
            if(self.MyQueue.flag()):
                self.p=self.MyQueue.getP()

            self.MyQueue.add(flag)
            #TODO remove it
            print('rank:',rank,'T:',self.T,'position:',self.position,'energy:',self.energy,'theta:',self.theta,'R:',self.R,'flag:',flag,'p',self.p)
            sys.stdout.flush()

        #MPI allgather, EnergyStatus records all core's energy information, StopStatus records any core wanting to stop
        EnergyStatus=np.array(comm.allgather(self.energy))
        EnergyStatus=self.energyC*(EnergyStatus-np.min(EnergyStatus))
        StopStatus=np.array(comm.allgather(self.myStopQueue.isstop()))
        # print(rank,'flag 1')
        # sys.stdout.flush()
        comm.barrier()

        #if any core wants to stop, then do it
        if(np.any(StopStatus)):
            return(0)
        # print(rank,'flag 2')
        # sys.stdout.flush()
        #the possibility every core jump to the condition of other core    
        JumpPossibility=np.exp(-1*EnergyStatus/self.T)/np.sum(np.exp(-1*EnergyStatus/self.T))
        RandomNumber=random.random()
        JumpPossibilitySum=np.array([np.sum(JumpPossibility[:i+1]) for i in range(self.CpuNumber)])
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
        aR=len(countDic)/self.CpuNumber
        self.R=int(self.R*np.exp(2*np.log(2)*(aR-0.5)))+1
        
        #MPI send all the information between two cores related to exchange, the tag is specially numbered
        SendCount=0
        # print(rank,'flag 5',NewPositionInformation,JumpPossibility,JumpPossibilitySum)
        # sys.stdout.flush()
        TagTemp=10**(len(str(self.CpuNumber))) 
        for i,value in enumerate(NewPositionInformation):
            if(value==rank and i!=rank):

                comm.isend(self.position, dest=int(i), tag=1*(TagTemp**2)+i*TagTemp+rank)
                comm.isend(self.energy, dest=int(i), tag=2*(TagTemp**2)+i*TagTemp+rank)
                comm.isend(self.theta, dest=int(i), tag=3*(TagTemp**2)+i*TagTemp+rank)
                comm.isend(self.MyQueue,dest=int(i), tag=4*(TagTemp**2)+i*TagTemp+rank)

        if(flag!=rank):

            self.position=comm.recv(source=int(flag), tag=1*(TagTemp**2)+rank*TagTemp+flag)
            self.energy=comm.recv(source=int(flag), tag=2*(TagTemp**2)+rank*TagTemp+flag)
            self.theta=comm.recv(source=int(flag), tag=3*(TagTemp**2)+rank*TagTemp+flag)
            self.MyQueue=comm.recv(source=int(flag), tag=4*(TagTemp**2)+rank*TagTemp+flag)
        # print(rank,'flag 6')
        # sys.stdout.flush()

        comm.barrier()
        return(1)

    def initEnvironment(self,configFileName='./config.ini'):
        self.configParse(configFileName)
        
        self.TotalNumberCount=0

        self.MyQueue=ItemStore(self.ItemStoreSize)
        self.myStopQueue=stopQueue(self.ParameterNumber,self.stopRepeateTimes,self.stopMoveStep)
        self.position=self.RandomInit()
        if(self.useBash):
            self.energy=self.f(self.position)
        else:
            self.energy=self.objectFunction(self.position)
            # print('flag 1')
            # sys.stdout.flush()

        self.p=0.44

    def initRepeate(self):
        # print(rank,self.InitLoopTime)
        # sys.stdout.flush()
        if(rank==0):
            commMaster.send(self.InitLoopTime,dest=0,tag=0)
        # print(rank,'flag')
        # sys.stdout.flush()
        ddcount=0
        for i in range(self.InitLoopTime):
            ddcount+=1
            #initial interation without temprature drops
            # print(rank,'flag2',ddcount)
            # sys.stdout.flush()
            flag=self.Step(0)
            # print(rank,'flag3',ddcount)
            # sys.stdout.flush()
            #recalculate acceptance rate to adjust moving step
            if(self.MyQueue.flag()):
                self.p=self.MyQueue.getP()
            self.MyQueue.add(flag)
            comm.barrier()
            # print(rank,'flag4',ddcount)
            # sys.stdout.flush()
            print('rank:',rank,'T:',self.T,'position:',self.position,'energy:',self.energy,'theta:',self.theta,'R:',self.R,'flag:',flag,'p',self.p)
            sys.stdout.flush()
        
    def endEnvironment(self):
        if(rank==0):
            commMaster.send(0,dest=0,tag=0)
        self.finalPositionInformation=comm.allgather(self.position)
        self.finalEnergyInformation=comm.allgather(self.energy)



if(__name__=='__main__'):
    commMaster = MPI.Comm.Get_parent()
    comm = MPI.COMM_WORLD 
    rank = comm.Get_rank()
    size = comm.Get_size()
    # print(rank,'dd')
    # sys.stdout.flush()
    sa=SA()
    sa.setObjectFunction()
    sa.initEnvironment()
    logging.basicConfig(filename=sa.logFileName, level=logging.INFO)

    if(rank==0):
        StartTime = time.asctime( time.localtime(time.time()) )
        logging.info('cpu numbers:'+str(sa.CpuNumber))
        logging.info('command name:'+sa.CommandName)
        logging.info('parameter numbers:'+str(sa.ParameterNumber))
        for i,j in zip(sa.RangeLow,sa.RangeHigh):
            logging.info('range: '+str(i)+'~'+str(j))
        logging.info('start time at:'+StartTime)  

    sa.initRepeate()

    if(rank == 0):
        StartDropTime=time.asctime( time.localtime(time.time()) )
        logging.info('temprature start drop at:'+StartDropTime)

    MainFlag=1
    while(MainFlag==1 and sa.T>10e-8):
        sa.TotalNumberCount+=sa.R
        MainFlag=sa.ALoop()
   
    sa.endEnvironment()
    if(rank == 0):
        EndTime=time.asctime( time.localtime(time.time()) )
        logging.info('program stop at:'+EndTime)
        logging.info('accuracy:'+','.join(str(x) for x in sa.stopMoveStep))
        for i,j,k in zip(range(sa.CpuNumber),sa.finalPositionInformation,sa.finalEnergyInformation):
            logging.info('core order:'+str(i))
            logging.info('final position:'+','.join(str(x) for x in j))
            logging.info('final energy: '+str(k))

        # minEnergy=min(sa.finalEnergyInformation)
        # minPosition=sa.finalPositionInformation[sa.finalEnergyInformation.index(minEnergy)]
        # print(minEnergy,end=' ')
        # for i in minPosition:
        #     print(i,end=' ')
    commMaster.Gather(np.array([sa.energy]),None,root=0)
    commMaster.Gather(np.array(sa.position),None,root=0)

    commMaster.Disconnect()