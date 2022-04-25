# What's Cachex?
Cachex is a perfect-information two-player game played on an n × n rhombic, hexagonally tiled board, based on the strategy game Hex.
Two players (named Red and Blue) compete, with the goal to form a connection between the opposing sides of the board corresponding to their respective color.
If you're a University of Melbourne COMP30024 student on Semester 1 2022, refer to the spec provided for the full rules of the game!

## What's this program for?
This Pygame program will allow you to play full, capture-filled rounds of Cachex with either a human friend or your own AI
(yep, the exact same AI you'll be making for Part B of the COMP30024 project!), on all board sizes between 3 and 15.

## Example:
![](/img/example.png)
![](/img/example2.png)

## How to use the program
First, make sure you have Python 3 or higher and the Pygame library installed for the game to run properly.

Next, you need to add a functional player AI if you intend to run the game with AI enabled. To do so, simply replace
the existing player.py file with your own that contains the Player class with the three methods described in the project
spec (or you can just paste your code into this file). 

To start the game, just launch the main.py file. You can customise the size of the board (between 3 and 15) and enable/disable
playing against your AI in the game settings. As long as your AI makes valid moves (and there aren't any bugs I missed),
it should be smooth sailing once you hit that play button!

## And lastly..
Major credit goes to Andrii Denysenko, who wrote the Pygame program for the original Hex game
(which you can find here: https://github.com/ANDREYDEN/Hex-Game) that I mostly built this on.

Hopefully you'll find this program super useful for the project! I'll be super happy knowing this program helped make
some killer Cachex players, so do give this repo a star if you ended up using it. 
And of course, feel free to make your own local customisations on this code however you see fit.
(But please don't copy any of the code directly to use in your project submission, I'm providing this for testing purposes only.)

Good luck on the assignment!

