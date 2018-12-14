Given two integers a and b, how can we evaluate the sum a + b without using operators such as +, -,

int sum(int a, int b)  
{
 
}



Which one would you use and why:

A.
int sum(int a, int b)  
{ 
    char *p = a; 
    return (int)&p[b]; 
}

B.
int sum(int a, int b)  
{ 
    if (a & b == 0) 
      return a ^ b; 
    else 
      return sum(a ^ b, a & b << 1); 
}

C.
int sum(int a, int b)  
{ 
    return printf("%*c%*c", a, '\r', b, '\r'); 
}

They all are working:

1. B would be my choice
Even B is not that straight forward, but at least it gives ideas about bitwise logic 
you have to refresh C/C++ binary opereation for B 

2.
A and C are smart and look like hacks 
if are looking for obfuscated C code contest it is here ioccc.org
