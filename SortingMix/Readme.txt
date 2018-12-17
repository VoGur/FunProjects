Both: .NET C# sort() and C++ STL  std::sort() 
------------------------------------------
using a 3-part hybrid sorting algorithm: 
"Introsort" or "Introspective sort" which is quicksort and heap sort hybrid plus insertion sort for small datasets.
The implementation required to be O(n log n) in complexity and is not not required to be stable.
Logic as follows:
If the partition size is fewer than 16 elements, it uses an insertion sort algorithm.
If the number of partitions exceeds 2 * LogN, where N is the range of the input array, it uses a Heapsort algorithm.
Otherwise, it uses a Quicksort algorithm.

Cut-off 16 for switching from quick sort to insertion sort, 
and 2*logN for switching from quick sort to heap sort chosen 
empirically as an approximate because of various tests and researches conducted.


Python  and Java non primitives sort()
--------------------------------------------
using
"Timsort" which is combination of mergesort and insertion sort
NOTE:
For primitives Java uses optimized quicksort ( below)


-----------------------------------------------
Sorting algorithms basics
-----------------------------------------------
# Top 3 used separately or in combination in implementations of languages or DB engines  

 "Quicksort"
All well around, in place sort algorithm.
Large generic unsorted datasets
Usually is fastest on arrays provided the pivot is chosen randomly
Worst case purely empirical n^2.
Not all Quicksort implementations are stable.
For Guaranteed performance use Heap sort.
Better performance for data allocated in memory than in "Merge"

Best O(n * log n).
Average O(n * log n).
Worst case O(n^2)
Space O(log n)


"Merge" 
Better performance for distributed data
as it is received from a network connection
or sorting data structures which don't allow efficient random access like linked lists than in "Quicksort"
Presorted sets works best on linked lists
Consumes more memory than "Quicksort"

Best O(n * log n).
Average O(n * log n).
Worst case O(n * log n).
Space O(n)


"Heapsort"  
Is probably the slowest out of three 
Not stable because operations on the heap can change the relative order of equal items.
Generic unsorted datasets, in place
Guaranteed performance O(n * log n).
Used in DB sorting

Best O(n * log n).
Average O(n * log n).
Worst case O(n * log n).
Space O(1)

--------------------------------- Slow main algorithms --------------------------------

"Insertion" simple to implement, in place, best for small dataset
Best O(n).
Average O(n^2) 
Worst case O(n^2) 
Space O(1) 


"Selection" in place
if for some reason Writes are incredibly expensive relative to Reads, then you might actually want 
Best O(n^2) 
Average O(n^2) 
Worst case O(n^2)
Space O(1) 


"Buble" sort Slower than insertion , not practical to use( research  only), in place
Best O(n^2)
Average O(n^2) 
Worst case O(n^2) 
Space O(1) 



Code to follow
