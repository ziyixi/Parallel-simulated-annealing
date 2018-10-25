# Parallel-simulated-annealing
### Code Author: Ziyi Xi(xiziyi2015@gmail.com)
### Algorithms' Authors: Zhihao Lou(zhlou@uchicago.edu), John Reinitz(reinitz@galton.uchicago.edu)
A python interface of Parallel simulated annealing algorithms, converts from:

> Lou Z, Reinitz J. Parallel simulated annealing using an adaptive resampling interval[J]. Parallel computing, 2016, 53: 23-31.
> Chu K W, Deng Y, Reinitz J. Parallel simulated annealing by mixing of states[J]. Journal of Computational Physics, 1999, 148(2): 646-662.


## Introduction
It's part of the graduation thesis of my dual major: computer science. 

Here are mainly two parts of the program. The first one is to realize the algorithm using mpi4py, namely mpi for python. I have made some changes of the raw algorithms to control the possible boundary problem and other problems. The second one is an interface for different programming languages. As for Python and Julia, you can simply call the function SA() of the init.py in the root directory, simply pass the object function. However, for Matlab users, you might have to copy all the document in the matlab directory to your matlab root directory (namely the forward model in),  and design a matlab function which receives parameters and return the value of the object function. Thus you should use python to call the init.py, namely:
```
python init.py
```
And change the end part of init.py to:
```
if(__name__=='__main__'):
    SA(functionName='Forward')
```
Here Forward should be the name of your function designed. If you want to use C++ or Fortran, please refer to test section: ctypes. You could wrap your code using ctypes or something else in python, and regard it as a pure python ufunc. 

What's more, In the Procedural programming directory, you could use:
```
mpiexec -n <CPU numbers in your config section> python test.py
```
to call any function you design as long as it receive parameters from the command line in order and print the object value to the command line.

## Config file
Here is the full config file:
```
[algorithms]
#The speed of reducing temperature
TLambda=0.001
#The speed of moving step change
K=1
#The coefficient of moving step
C=1
#Initial temperature
T=5000
#Initial time interval for information of different cores to exchange
R=300
#Initial time for selecting random initial position and step adjustment
InitLoopTime=100
#The time interval to renew the acceptance rate p, larger ItemStoreSize will reduce the accuracy of the final result and enlarge the time consumed, but less ItemStoreSize will make the program unstable
ItemStoreSize=10

[system]
#The number of processors used, using mpiexec -n <CpuNumber> python main.py 
CpuNumber=4

[model]
#The dimension of the parameter space
ParameterNumber=4
#The upper barrier of the parameter space, using inf if no barrier defined
RangeHigh=16,36,3.7,4.4
#The lower barrier of the parameter space, using -inf if no barrier defined
RangeLow=6,26,2.7,3.4
#if inf or -inf, at least give a range of [-setrange,setrange]
setrange=1
#The command name of the forward program. Since just writing a small code will enable feathers such as ./a 2 3 4, in which 2,3,4 are parameters input, and the program return a simple value such as 222.344 as the object value that need to be optimized.
CommandName=./ignore this part
#sensity of different parameters. If you want to move a parameter more quickily, just enlarge the value accordingly
sensity=1,1,0.1,0.1
#Initial moving step, not matter actually
stopMoveStep=0.001,0.001,0.0001,0.0001
#criterio of stoping. Any core which moves its step less than theta for stopRepeateTimes times will cause the program to end
stopRepeateTimes=40
#initial moving step for sensity=1
theta=0.01
#Control the sensity of energy change
energyC=1
#Control the name of the logfile
logFileName=logfile
```

I believe the main config you might want to change is CpuNumber(numbers of the cores you want to use when called from Python and Julia, also around 3/2 cores you want to call in Matlab), ParameterNumber(Numbers of your parameter), RangeHigh, RangeLow, and CommandName(if you receive and print values to the command line), sensity(the relative value of the moving step you wish for each parameter), stopMoveStep, logFileName. You could also change the initial temperature T if you like. 

Finally, when the program terminates, it will return values as the form:
```
finalenergy parameter1 parameter2 parameter3
```
and a log file recording status and final result of each core, the return value mentioned above is simply the smallest one. You might also redirect the output of each step by using:
```
python init.py > mylog
```

## Install and setup
Here are necessary python modules you need:

numpy, mpi4py, matlab.

I suggest you install an Anaconda, and use:
```
conda install numpy
pip install mpi4py
conda install -c mpi4py openmpi 
```
Remember, don't use conda to install mpi4py, because as mpich doesn't support dynamic processes, I have to use openmpi. But the mpi4py version of anaconda is bind to mpich.

And if you use matlab, please refer to http://cn.mathworks.com/help/matlab/matlab-engine-for-python.html to install Matlab engine for python.

Good luck! If you are a skilled python user, I believe you could be familar with the procedures.

## Possible Problems
If you encounter any problems, please feel free to contact me(xiziyi2015@gmail.com). And if your Matlab version is too old, it may consume too much memory. According to my test, if I use Matlab R2017b, with a 16G memory in my computer, it could start with around 8 CpuNumbers. But as for the machine in my laboratory, with a Matlab version of R2015a, the memory of 128G could simply support 10 CpuNumbers or it will raise problems.

## Acknowledgement
1. Thanks to Prof. Guangzhong Sun, who is the mentor of the thesis. 
2. Thanks to Prof. Daoyuan Sun, who gave me this topic to solve. 
3. Thanks to Dr. Xinghua Jia, who gave me the test function of Matlab.
4. Thanks to my roommate Sixue Xu, who gave me inspiration of the algorithm.
