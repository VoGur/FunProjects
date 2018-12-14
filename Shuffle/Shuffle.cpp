// Shuffle.cpp : Defines the entry point for the console application.

#include "stdafx.h"
#include <random>
#include <algorithm>
#include <iterator>
#include <iostream>
#include <chrono>      

using namespace std;


//used STL's random_shuffle  which relies on 
//Knuth Fisher - Yates shuffle O(n)
//NOTE:
//standard generators defined in <random>
void shuffle_vector(vector<int> & v) {
	unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
	cout << "Seed : " << seed << endl;
	shuffle(v.begin(), v.end(), default_random_engine(seed));

}

int main()
{
	int vSize;

	//Get a number
	cout << "Enter an integer:\n>";
	cin >> vSize;
	cout << "You entered: " << vSize << '\n';

	//Populate vector
	vector<int> v;
	for (int i = 1; i <= vSize; i++)
		v.push_back(i);

	//STD shuffle wrapper 
	shuffle_vector(v);
	
	//Output
	cout << "Shuffled elements:";
	for (int& x : v) cout << ' ' << x;
	cout << '\n';

    return 0;
}
