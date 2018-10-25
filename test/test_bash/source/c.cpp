#include<iostream>
#include<cmath>
#define PI  3.14159265358979323846
using namespace std;

int main()
{
    double x1,x2,f;
    cin>>x1>>x2;
    f=-20*exp(-0.2*sqrt(0.5*(x1*x1+x2*x2)))-exp(0.5*(cos(4*x1)+cos(4*x2)))+20+exp(1);
    cout<<f;
}