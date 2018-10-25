#include<iostream>
#include<cmath>
#define PI  3.14159265358979323846
using namespace std;

int main()
{
    double x1,x2,f;
    cin>>x1>>x2;
    f=100*((pow(sin(pow(x1,2)-pow(x2,2)),2)-0.5)/pow((1+0.001*(x1*x1+x2*x2)),2)-0.5);
    cout<<f;
}