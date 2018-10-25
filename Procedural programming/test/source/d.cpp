#include<iostream>
#include<cmath>
#define PI  3.14159265358979323846
using namespace std;

int main()
{
    double x1,x2,x3,x4,f;
    cin>>x1>>x2>>x3>>x4;
    f=-20*exp(-0.2*sqrt(0.25*(x1*x1+x2*x2+x3*x3+x4*x4)))-exp(0.25*(cos(4*x1)+cos(4*x2)+cos(4*x3)+cos(4*x4)))+20+exp(1);
    cout<<f;
}