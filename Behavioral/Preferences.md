Given two integers a and b, how can we evaluate the sum a + b without using operators such as +, -,

int sum(int a, int b)  
{
 
}



Which one would you use :

A.
int sum(int a, int b)  
{ 
    char *p = a; 
    return (int)&p[b]; 
}

B.
int sum(int a, int b)  
{ 
    int s = a ^ b; 
    int carry = a & b; 
  
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

B because if are looking for obfuscated C code contest it is here ioccc.org
