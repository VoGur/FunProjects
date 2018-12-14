using RockPprScs;
using System;

namespace RockPprScs
{
    enum RockPaperScissors
    {
        Rock = 1,
        Paper,
        Scissors
    };

    // Outcomes in reference to the player
    enum Outcomes
    {
        Won, 
        Lost,
        Tie
    };
 
    class Program
    {
        static void Main(string[] args)
        {

            bool keepPlaying = true;

            while (keepPlaying)
            {
                DetermineWinner(PlayerChoice(), MachineChoice());

                Console.WriteLine("New game? y/n");
                ConsoleKeyInfo key = Console.ReadKey(); //wait for player to press a key
                keepPlaying = key.KeyChar == 'y'; //continue only if y was pressed
            }
        }

        private static void  DetermineWinner(int player, int machine) {
            /* User winning logic
            ***************************
                        Machine
            U        Rock    Ppr    Scs
            s  Rock  tie     lost   won 
            e  Ppr   won     tie    lost   
            r  Scs   lost    won    tie 
            ***************************/
            Outcomes[,] WinLogic = new Outcomes[,]
            {
            {Outcomes.Tie, Outcomes.Lost, Outcomes.Won },
            {Outcomes.Won, Outcomes.Tie, Outcomes.Lost },
            {Outcomes.Lost ,Outcomes.Won  , Outcomes.Tie }
            };


            switch (WinLogic[player, machine])
            {
                case Outcomes.Tie:
                    Console.Write($"It  is a tie.\n"); break;
                case Outcomes.Won:
                    Console.Write($"You won.\n"); break;
                case Outcomes.Lost:
                    Console.Write($"You lost.\n"); break;
            }
        }

        //returns col index [0-2] for the matrix with winning logic 
        private static int MachineChoice()
        {

        Random rand = new Random();
            int selection = rand.Next(0, 3);
            Console.Write($"Machine choice: {((RockPaperScissors)(selection + 1)).ToString()}\n");
            return selection;
        }

        //returns row index [0-2] for the matrix with winning logic 
        private static int PlayerChoice()
        {
            int selection;
            do
            {
                Console.Write("\nRock ,Paper or Scissors ?\n");
                Console.Write("Enter 1 ,2 or 3 : ");
                Int32.TryParse(Console.ReadLine(),out selection);
            } while (!Enum.IsDefined(typeof(RockPaperScissors), selection));
            Console.Write($"Player choice: {((RockPaperScissors)selection).ToString()}\n");
            return selection - 1;
        }
    }
}
