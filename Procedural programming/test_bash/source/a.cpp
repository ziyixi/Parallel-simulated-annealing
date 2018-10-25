#include<iostream>
#include<cmath>
using namespace std;
#define PI  3.14159265358979323846
int main()
{
    double x1,x2,ras;
    cin>>x1>>x2;
    ras=20+pow(x1,2)+pow(x2,2)-10*(cos(2*PI*x1)+cos(2*PI*x2));
    cout<<ras;
}
         