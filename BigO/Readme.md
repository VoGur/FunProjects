Explain Big O "in plain english".
A way to explain how solution performance and/or memory allocation depend on number of elements. 

O(1)

action()
or
action();action();action()


O(n)

for ( int i = 1 ; i<n; i++)\{
 action()
\}


O(LogM(n))

for ( int i = 1 ; i<n; i=i*M)\{
 action();
\}

NOTE: where M is base, say for 2
-----------------
i       iterations
-----------------
1       1
4       2
8       3
16      4
....
1024    16


O(n^2) 

for ( int i = 1 ; i<n; i++)\{
	for ( int y = 1 ; y<n; y++)\{
	  action();
	\}
\}

O(n^3) 

for ( int i = 1 ; i<n; i++)\{
	for ( int j = 1 ; j<n; j++)\{
		for ( int y = 1 ; y<n; y++)\{
		  action();
		\}
	\}
\}
