// OMAHACOMP.cpp : This file contains the 'main' function. Program execution begins and ends there.
//Copyright Vadim Voronin 2018

#include <iostream>
#include <fstream>
#include <regex>
#include <string>
#include <random>     
#include <tuple>      
#include <map>

using namespace std;

const int DECK_SIZE = 52;
const int HAND_SIZE = 5;
const int BOARD_SIZE = 5;
const int HOLE_CARDS = 4;
const int NUMBER_OF_PLAYERS = 2;

const int SUITS = 4;
const int RANKS = 13;
const int SCORES = 9;

enum suits {
	DIAMONDS,
	HEARTS,
	CLUBS,
	SPADES
};
enum handScores
{
	HIGH_CARD,
	ONE_PAIR,
	TWO_PAIR,
	THREE_OF_A_KIND,
	STRAIGHT,
	FLUSH,
	FULL_HOUSE,
	FOUR_OF_A_KIND,
	STRAIGHT_FLUSH
};


char  nameSuite[SUITS] = { 'd', 'h','c','s' };
char const nameRank[RANKS] = { '2','3','4','5','6','7','8','9','T','J','Q','K','A' };

char const *nameHand[SCORES] =
{
	"High Card",
	"One Pair",
	"Two Pair",
	"3-of-a-Kind",
	"Straight",
	"Flush",
	"Full House",
	"4-of-a-Kind",
	"Straight Flush"
};

enum Results{
	TIE,
	PLAYER1,
	PLAYER2
};


//patterns guarantied to be in the file 
string ptrnA("HandA:");
string ptrnB("HandB:");
string ptrnBrd("Board:");
//read # characters after each pattern to get cards 
int cardsPlLen = 11;
int cardsBrdLen = 14;

//Just to avoid searching in nameSuite/nameRank arrays 
map<char, int> ranks = { {'2',0},{'3',1},{'4',2},{'5',3},{'6',4},{'7',5},{'8',6},{'9',7},{'T',8},{'J',9},{'Q',10},{'K',11},{'A',12} };
map<char, int> suits = { {'d',0},{'h',1},{'c',2},{'s',3} };

//3 out of 5 community cards
vector<vector<int>>  Choose_5_3() {
	vector<vector<int>> combinations;
	vector<int> entry(3);
	for (int i1_vv = 0; i1_vv < 5; ++i1_vv) {
		for (int i2_vv = i1_vv + 1; i2_vv < 5; ++i2_vv) {
			for (int i3_vv = i2_vv + 1; i3_vv < 5; ++i3_vv) {
				//cout << i1 << " " << i2 << " " << i3 << " \n";
				entry[0] = i1_vv; entry[1] = i2_vv; entry[2] = i3_vv;
				combinations.push_back(entry);
			}
		}
	}
	return combinations;
}
//2 out 4 hole cards
vector<vector<int>>  Choose_4_2() {
	vector<vector<int>> combinations;
	vector<int> entry(2);
	for (int i1_vv = 0; i1_vv < 4; ++i1_vv) {
		for (int i2_vv = i1_vv + 1; i2_vv < 4; ++i2_vv) {
			//cout << i1 << " " << i2 << " \n";
			entry[0] = i1_vv; entry[1] = i2_vv;
			combinations.push_back(entry);
		}
	}
	return combinations;
}



class Card {
public:
	int r_vv;
	int s_vv;

	Card(int suit = 0, int rank = 0) : r_vv(rank), s_vv(suit) {};

	//sorting cards
	bool operator<(const Card & card)
	{
		return std::tie(r_vv, s_vv) < std::tie(card.r_vv, card.s_vv);
	}

	bool operator==(const Card & card) const
	{
		return r_vv == card.r_vv;
	}

	friend ostream& operator<<(ostream& os, const Card& crd)
	{
		os << "  " << nameRank[crd.r_vv] << nameSuite[crd.s_vv];
		return os;
	}
};

class Hand {
private:
	int hScore = 0;				//hand highest combination
	int hRank = 0;				//highest combination card rank
	vector<Card> hKickers;		//keep kicker cards to compare

public:

	tuple <int, int, vector<Card>> getScore() {
		showBestHand();
		return make_tuple(hScore, hRank, hKickers);
	}

	void clear() {
		hScore = 0;
		hRank = 0;
		hKickers.clear();
	}

	//update if it is a better hand 
	bool updateScore(int score, int rank, vector<Card> &kickers) {
		bool st = false;
		if (score > hScore) {
			hScore = score;
			hRank = rank;
			hKickers = kickers;
			st = true;
		}
		else if (score == hScore) {
			if (rank > hRank) {
				hRank = rank;
				hKickers = kickers;
				st = true;
			}
			else if (rank == hRank) {
				pair <vector<Card>::iterator, vector <Card>::iterator> mispair;
				mispair = mismatch(kickers.begin(), kickers.end(), hKickers.begin());
				//if it is not past-the-end-iterator vectors differ 
				if (mispair.first != kickers.end() && mispair.first->r_vv > mispair.second->r_vv) {
					hKickers = kickers;
					st = true;
				}
			}
		}
		if (st) {
			cout << " => HIGHER SCORE UPDATED\n\n";
			showBestHand();
		}
		return st;
	}

	void showBestHand()
	{
		if (!hKickers.empty()) {
			cout << "\n------------------------------------------------------------------\n";
			cout << "                      Best hand score :\n";
			showScore(hScore, hRank, hKickers);
			cout << "\n------------------------------------------------------------------\n";
		}
	}

	void showScore(int score, int rank, vector<Card> &kickers) const
	{

		cout << " Hand score : " << score << "(" << nameHand[score] << ")";
		cout << " Hand highest rank : \"" << nameRank[rank] << "\"";
		cout << " Kickers cards(ranks):";
		for (Card& crd : kickers) cout << crd;
		cout << "\n";
	}


	//return uniform kickers cards (array of 4)  for all the combinations
	vector<Card> getKickers(vector<Card> mrg, int rank1, int rank2 = -1) {
		vector<Card> kickers;
		//rank2 is the rank of pair or second pair in "two pairs" and "full house" : insert first 
		if (rank2 != -1)
			kickers.push_back(Card(0, rank2));
		//add elements which will be analyzed when compare hands with the same rank
		copy_if(mrg.begin(), mrg.end(), back_inserter(kickers), [&rank1, &rank2](Card n) {return (n.r_vv != rank1 && n.r_vv != rank2); });
		// skip sorting for "two pairs" and "full house"
		if (rank2 == -1)
			sort(kickers.rbegin(), kickers.rend());
		//uniformed kickers returned
		while (kickers.size() < 4)
			kickers.push_back(Card());
		return kickers;
	}

	//check whether sorted vector contains only unique elemnts in range 
	bool isDistinct(std::vector<Card> mrg, int begin, int end) {
		for (int i = begin; i < end; i++) {
			if (mrg[i].rank == mrg[i + 1].rank)
				return false;
		}
		return true;
	}

	//Input: 5 sorted cards combination
	//Return : Score, Rank,  4 kickers uniformed vector    
	//Scores:
	//8 straight flush  
	//5 flush  

	int flushCombinations(std::vector<Card> mrg) {
		int score = FLUSH;
		int rank = 0;
		vector<Card> kickers;

		//Do we have five sequential cards 
		bool seqCards5 = (isDistinct(mrg, 0, 4) && (mrg[4].rank - mrg[0].rank) == 4) ? true : false;
		//Do we have four sequential cards 
		int seqCards4 = (isDistinct(mrg, 0, 3) && (mrg[3].rank - mrg[0].rank) == 3) ? true : false;


		//Check for straight flush :
		if (seqCards5 || seqCards4) {
			//If we have five cards in sequential order
			if (seqCards5)
			{
				score = STRAIGHT_FLUSH;
				rank = mrg[4].rank;
				kickers = getKickers(mrg, rank);
			}
			//if we have 4 cards in sequential order check if it is special case 2-3-4-5-A
			else
				if (seqCards4 && mrg[0].rank == 0 && mrg[4].rank == 12) {
					cout << " Straight with Ace lowest\n";
					score = STRAIGHT_FLUSH;
					rank = 3; //it is lowest straight "5"
					kickers = getKickers(mrg, rank);
				}
		}
		else {
			rank = mrg[4].rank;
			kickers = getKickers(mrg, rank);
		}

		showScore(score, rank, kickers);
		updateScore(score, rank, kickers);

		return score;
	}

	//Input: 5 sorted cards combination and array of ranks
	//Return : Score, Rank,  4 kickers uniformed vector    
	//Scores:
	//7 Four of a kind  
	//6 Full house
	//4 Straight
	//3 Three of a kind 
	//2 two pairs 
	//1 one pair 
	//0 single highest card
	int otherCombinations(std::vector<Card> mrg, int *sameRankCount) {
		int rank = 0;
		int score = HIGH_CARD;
		vector<Card> kickers;

		int twoCount = 0;
		int threeCount = 0;
		int fourCount = 0;

		int twoCountRank[2] = { 0 }; //to keep 2 pairs rank
		int threeCountRank = 0;
		int fourCountRank = 0;

		//same rank count
		for (int i = 0; i < RANKS; ++i)
		{
			if (sameRankCount[i] == 2)
			{
				twoCountRank[twoCount] = i;
				++twoCount;
				cout << " -> found 2 cards of the same rank  " << nameRank[i] << "\n";
			}
			else if (sameRankCount[i] == 3)
			{
				++threeCount;
				threeCountRank = i;
				cout << " -> found 3 cards of same rank " << nameRank[i] << "\n";
			}
			else if (sameRankCount[i] == 4)
			{
				++fourCount;
				fourCountRank = i;
				cout << " -> found 4 cards of the same rank " << nameRank[i] << "\n";
			}
		}

		//Do we have five sequential cards 
		bool seqCards5 = (isDistinct(mrg, 0, 4) && (mrg[4].rank - mrg[0].rank) == 4) ? true : false;
		//Do we have four sequential cards 
		int seqCards4 = (isDistinct(mrg, 0, 3) && (mrg[3].rank - mrg[0].rank) == 3) ? true : false;

		//5 cards of any suit in sequential order
		if (seqCards5)
		{
			score = STRAIGHT;
			rank = mrg[4].rank;
			kickers = getKickers(mrg, rank);
		}
		//4 cards of any suit in sequential order, check if it is 2-3-4-5-A
		else if (seqCards4 && mrg[0].rank == 0 && mrg[4].rank == 12)
		{
			cout << " Straight with Ace lowest\n";
			score = STRAIGHT;
			rank = 3; //it is lowest straight - highest is "5"
			kickers = getKickers(mrg, rank);
		}
		//Any four numerically matching cards
		else if (fourCount == 1)
		{
			score = FOUR_OF_A_KIND;
			rank = fourCountRank;
			kickers = getKickers(mrg, rank);
		}
		else if (threeCount == 1)
		{   //Combination of three of a kind and a pair in the same hand
			if (twoCount == 1)
			{
				score = FULL_HOUSE;
				rank = threeCountRank;
				// rank of the pair passed as last prm
				kickers = getKickers(mrg, rank, twoCountRank[0]);
			}
			//Any three numerically matching cards
			else
			{
				score = THREE_OF_A_KIND;
				rank = threeCountRank;
				kickers = getKickers(mrg, rank);
			}
		}
		//Two pairs in the same hand
		else if (twoCount == 2)
		{
			score = TWO_PAIR;
			// rank of the lowest pair passed as last prm
			rank = twoCountRank[0];
			if (twoCountRank[1] > twoCountRank[0]) {
				rank = twoCountRank[1];
				twoCountRank[1] = twoCountRank[0];
			}
			kickers = getKickers(mrg, rank, twoCountRank[1]);
		}
		//Any two numerically matching cards
		else if (twoCount == 1)
		{
			score = ONE_PAIR;
			rank = twoCountRank[0];
			kickers = getKickers(mrg, rank);
		}
		else if (score == HIGH_CARD)
		{
			rank = mrg[4].rank;
			kickers = getKickers(mrg, rank);
		}

		showScore(score, rank, kickers);
		updateScore(score, rank, kickers);

		return score;
	}


	int scoreHand(vector<Card> hole, vector<Card> community) {

		int score = HIGH_CARD;
		int sameRankCount[RANKS] = {};
		int sameSuitCount[SUITS] = {};

		if (hole.size() + community.size() > HAND_SIZE)
			throw std::invalid_argument("Hand size cannot exceed {1} cards", HAND_SIZE);

		//merge community cards with hole cards
		std::vector<Card> mrg;
		mrg.reserve(hole.size() + community.size());
		mrg.insert(mrg.end(), hole.begin(), hole.end());
		mrg.insert(mrg.end(), community.begin(), community.end());

		for (Card& crd : mrg) cout << crd;
		cout << " -> sorted hand ->";
		//sort rank/suit tuples
		std::sort(mrg.begin(), mrg.end());
		for (Card& crd : mrg) cout << crd;
		cout << "\n";

		//stats
		for (size_t i = 0; i < mrg.size(); ++i)
		{
			sameRankCount[mrg[i].rank]++;
			sameSuitCount[mrg[i].suit]++;

		}

		//Check for flush 
		bool flush = false;
		for (int i = 0; i < SUITS; ++i)
		{
			//Five cards of the same suit, in any order
			if (sameSuitCount[i] == HAND_SIZE)
				flush = true;
		}

		if (flush) {
			score = flushCombinations(mrg);
		}
		else {
			score = otherCombinations(mrg, sameRankCount);
		}

		return score;
	};

};

class Player {
private:
	std::vector<Card> hole; //cards dealt 
	Hand hand;
public:
	Player(){};


	tuple <int, int, vector<Card>> getCompleteScore() {
		return hand.getScore();
	}

	string getScore() {
		tuple <int, int, vector<Card>> p = hand.getScore();
		int score = get<0>(p);
		int rank = get<1>(p);
		vector<Card> kickers = get<2>(p);
		return "(" + string(nameHand[score]) + ")";
	}


	void addCard(Card card)
	{
		if (hole.size() < HOLE_CARDS)
			hole.push_back(card);
		else
			throw std::invalid_argument("Number dealt cards cannot exceed {1}", HOLE_CARDS);
	}

	// expected sequence similar to Ac-Kd-Jd-3d 
	void loadCardsFromFile(string cards)
	{
		hole.clear();
		hand.clear();
		for (int i = 0; i < HOLE_CARDS; i++) {
			hole.push_back(Card(suits[cards.at(i*3+1)], ranks[cards.at(i*3)]));
		}

	}

	void findBestHand(const vector<Card> &community)
	{

		vector<Card> useHoleCards;
		vector<Card> useComCards;
		int combCntr = 0;

		cout << "\n-------------Player all possible hand combinations --------\n";

		//check combinations of any 2 hole cards and any 3 from community cards 
		for (vector<int>& hCrd : Choose_4_2()) {
			useHoleCards.push_back(hole[hCrd[0]]);
			useHoleCards.push_back(hole[hCrd[1]]);

			for (vector<int>& cCrd : Choose_5_3()) {
				combCntr++;
				useComCards.push_back(community[cCrd[0]]);
				useComCards.push_back(community[cCrd[1]]);
				useComCards.push_back(community[cCrd[2]]);

				cout << "\n------------- Hand combination #" << combCntr <<"--------\n";
				cout << " Using 3 cards with index : " << cCrd[0] << " " << cCrd[1] << " " << cCrd[2] << " ";				
				cout << "from community cards : "; 
				for (Card crd : community) cout << crd; cout << " Cards : ";
				for (Card& crd : useComCards) cout << crd; cout << "\n";
				 

				cout << " Using 2 player cards with index :" << hCrd[0] << " " << hCrd[1] << " ";				
				cout << "from player cards : ";
				for (Card crd : hole) cout << crd; cout << " Cards : ";
				for (Card crd : useHoleCards) cout << crd; cout << "\n";
	
				//score 2 hole cards and 3 from community
				hand.scoreHand(useHoleCards, useComCards);
				useComCards.clear();
			}
			useHoleCards.clear();
			hand.showBestHand();
		}
	}
};

//compare 2 players scores which is a combination of hand score, rank of the highest cards and kickers
//Returns one of : 0 in case of tie or  1 when 1-st player won , 2 - when 2-nd
int compareScores(tuple <int, int, vector<Card>> ph1, tuple <int, int, vector<Card>> ph2) {
	int st = PLAYER2;

	int score1 = get<0>(ph1);
	int rank1 = get<1>(ph1);
	vector<Card> kickers1 = get<2>(ph1);

	int score2 = get<0>(ph2);
	int rank2 = get<1>(ph2);
	vector<Card> kickers2 = get<2>(ph2);

	if (score1 > score2) {
		st = PLAYER1;
	}
	else if (score1 == score2) {
		if (rank1 > rank2) {
			st = PLAYER1;
		}
		else if (rank1 == rank2) {
			pair <vector<Card>::iterator, vector <Card>::iterator> mispair;
			mispair = mismatch(kickers1.begin(), kickers1.end(), kickers2.begin());
			//if it is not past-the-end-iterator vectors differ
			if (mispair.first != kickers1.end() && mispair.first->r_vv > mispair.second->r_vv) {
				st = PLAYER1;
			}
			else if (mispair.first == kickers1.end()){
				st = TIE;
			}
		}
	}
	return st;
}

// expected sequence similar to Ah-Kh-5s-2s-Qd
void loadBoardCardsFromFile(string cards, vector<Card> &shared)
{
	shared.clear();
	for (int i = 0; i < BOARD_SIZE; i++) {
		shared.push_back(Card(suits[cards.at(i * 3 + 1)], ranks[cards.at(i * 3)]));
	}

}


int main(int argc, char* argv[])
{



	std::vector<Card> shared;
	Player HandA;
	Player HandB;

	if (argc < 3) {
		std::cerr << "Usage: " << argv[0] << " inputFile" << " outputFile\n";
		return -1;
	}

	string line;
	ifstream inFile(argv[1]);
	ofstream outFile(argv[2]);

	if (inFile.is_open() && outFile.is_open()) {
		while (getline(inFile, line)) {
			//get cards	
			string A = line.substr(line.find(ptrnA) + ptrnA.length(), cardsPlLen);
			string B = line.substr(line.find(ptrnB) + ptrnB.length(), cardsPlLen);
			string Brd = line.substr(line.find(ptrnBrd) + ptrnBrd.length(), cardsBrdLen);

			HandA.loadCardsFromFile(A);
			HandB.loadCardsFromFile(B);
			loadBoardCardsFromFile(Brd, shared);

			//process hands
			HandA.findBestHand(shared);
			HandB.findBestHand(shared);
			int result = compareScores(HandA.getCompleteScore(), HandB.getCompleteScore());

			//original line and results
			outFile << "\n" << line << "\n";
			if (result == TIE) {
				outFile << "=> Split Pot " << HandA.getScore() << "\n"; //doesnt matter which hand to show
			}
			else if (result == PLAYER1) {
				outFile << "=> HandA wins " << HandA.getScore() << "\n";
			}
			else {
				outFile << "=> HandB wins " << HandB.getScore() << "\n";
			}
		}
		inFile.close();
		outFile.close();
	}
	else {
		if (inFile.failbit) {
			cout << " Couldn't open input file : " << argv[1] << "\n";
		}
		else {
			cout << " Couldn't open output file : " << argv[1] << "\n";
		}
		return -1;
	}
}


