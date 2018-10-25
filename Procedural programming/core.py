"""
A Simulated annealing framework for inverse
:copyright:
    ZIYI XI(xiziyi2015@gmail.com)
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

import config
import numpy as np
import random
import sys
import subprocess

def Step(T,position,energy,p,theta,f,sensity,initFlag):
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
    #control temprature
    if(initFlag==0):
        T=T
    else:
        T=(1-config.TLambda)*T
    
    #renew data 
    thetaNew=theta*np.exp(config.K*(p-0.44))
    deltaX=config.C*np.random.laplace(0,thetaNew,config.ParameterNumber)*sensity
    #moving
    positionNew=position+deltaX
    #boundary check
    for i,value in enumerate(positionNew):
        if(value<config.RangeLow[i]):
            return(T,position,energy,theta/1.93,2)
        if(value>config.RangeHigh[i]):
            return(T,position,energy,theta/1.93,2)
        
    energyNew=f(positionNew)
    #jump status
    if(energyNew<energy):
        return(T,positionNew,energyNew,thetaNew,0)
    else:
        possibility=np.exp(-(energyNew-energy)/T)
        if(possibility>random.random()):
            return(T,positionNew,energyNew,thetaNew,1)
        else:
            return(T,position,energy,thetaNew,2)

def RandomInit():
    '''
    an evenly distrution of [RangeLow,RangeHigh] 
    input: None

    output:
    ParameterNumber numbers from an evenly distrution of [RangeLow,RangeHigh] 
    '''
    result=np.zeros(config.ParameterNumber)
    for i in range(config.ParameterNumber):
        result[i]=(((self.RangeHigh[i]+self.RangeLow[i])/2-0.5)+random.random())*(self.RangeHigh[i]-self.RangeLow[i])
    for i,value in enumerate(result):
        if(value==np.inf or value==-1*np.inf):
            result[i]=(random.random()-0.5)*config.setrange
    return result

def Raw_function(parameters,command=''):
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

def f(parameters):
    '''
    The wrapper of the forward model
    input: parameters
    output: output value
    '''
    result=Raw_function(parameters,command=config.CommandName)
    return result

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
    def __init__(self):
        stopCount=0
        lasttimevalue=np.zeros(config.ParameterNumber)
    def isstop(self):
        if(self.stopCount>config.stopRepeateTimes):
            return True
        else:
            return False
    def valueadd(self,thistimevalue):
        if(np.all(thistimevalue-self.lasttimevalue<=config.stopMoveStep)):
            self.stopCount+=1
        else:
            self.stopCount=0
        self.lasttimevalue=thistimevalue
    def refresh(self):
        self.stopCount=0
        self.lasttimevalue=np.zeros(config.ParameterNumber)
