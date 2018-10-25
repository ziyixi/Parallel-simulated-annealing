import matlab.engine
import numpy as np
import sys

class PoolMatlab(object):
    def __init__(self,processes=1,functionName='test'):
        self.processes=processes
        self.functionName=functionName
        print('start 1')
        sys.stdout.flush()
        self.matlabEngines=[matlab.engine.start_matlab() for i in range(processes)]
        print('start 2')
        sys.stdout.flush()
    def map(self,parameters):
        self.commandName=['' for i in range(self.processes)]
        for i,parameter in enumerate(parameters):
            parameterList=''
            for j in parameter:
                parameterList+=str(j)+','
            parameterList='self.matlabEngines['+str(i)+'].'+self.functionName+'('+parameterList[:-1]+',async=True)'
            self.commandName[i]=parameterList

        futures=[eval(self.commandName[i]) for i in range(self.processes)]
        results=np.array([futures[i].result() for i in range(self.processes)])
        # print(futures)
        return results

if(__name__=='__main__'):
    pool=PoolMatlab(2,functionName='test')
    a=np.array([[1.0],[2.0]])
    print(pool.map(a))
