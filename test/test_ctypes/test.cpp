#include<iostream>
#include<cmath>
#define PI  3.14159265358979323846
using namespace std;

extern "C" double dog(double x1,double x2,double x3,double x4)
{
    double f;
    // cin>>x1>>x2>>x3>>x4;
    f=-20*exp(-0.2*sqrt(0.25*(x1*x1+x2*x2+x3*x3+x4*x4)))-exp(0.25*(cos(4*x1)+cos(4*x2)+cos(4*x3)+cos(4*x4)))+20+exp(1);
    // cout<<f;
    return f;
} 

int main()
{
    return 0;
}