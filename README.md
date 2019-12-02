# Farkle Fest 2k19

In this challenge, we will be playing the semi-popular dice game Farkle.

[Farkle](https://boardgamegeek.com/boardgame/3181/farkle) is a dice game that has players selecting to save dice or risk rerolling the die for more points to add to their total. Players should use probability, game-state considerations and opponent tendency to make their decisions.


## How to play

[Rules lifted from this PDF, which includes scoring. There are some differences that you should note after](https://www.elversonpuzzle.com/Farkle-instructions11.pdf)

> Each player takes turns rolling the dice. When it's your turn, you
> roll all six dice at the same time. Points are earned every time you
> roll a 1 or 5, three of a kind, three pairs, a six-dice straight
> (1,2,3,4,5,6), or two triplets.
> 
> If none of your dice earned points, that's a Farkle! Since you earned
> no points, you pass the dice to the next player.
> 
> If you rolled at least one scoring die, you can bank your points and
> pass the dice to the next player, or risk the points you just earned
> during this round by putting some or all of the winning die (dice)
> aside and rolling the remaining dice. The remaining dice may earn you
> additional points, but if you Farkle, you lose everything you earned
> during the round. 
>
> If all of your dice contribute to the score you re-roll
> the dice and add to the points already rolled, but a farkle will lose all the points, including rollover. This is called a "hot-streak"
> 
> Scoring is based only on the dice in each roll. You can earn points
> by combining dice from different rolls. You can continue rolling the
> dice until you either Pass or Farkle. Then the next player rolls the
> six dice until they Pass or Farkle. Play continues until it is your
> turn again.
> 
> The final round starts as soon as any player reaches 20,000 or more
> points.

Scoring:

>         five = 50
>         one = 100
>         triple 1 = 1000
>         triple 2 = 200
>         triple 3 = 300
>         triple 4 = 400
>         triple 5 = 500
>         triple 6 = 600
>         one thru six = 1500
>         three pairs = 1500
>         two triplets = 2500
>         four of a kind = 1000
>         five of a kind = 2000
>         six of a kind = 3000
>         farkle = 0
>         three farkles in a row = -1000

Notes:

* There are varying scoring tables. Use the one linked and rewritten above
* Most online versions say something like "You cannot earn points by combining dice from different rolls". This is ***not*** how I play. If you roll triple sixes and reroll and end up with another six you now have quad sixes.
* The ending score has been increased from 10,000 to 20,000. This increases the decision points and decreases randomness.
* Some variants have a "threshold to start getting points" (often around 500). This would prevent you from keeping a roll of less than 500 if your score was 0 (or negative). This rule is ***not*** in effect.


## Challenge


In this challenge, you will write a Python 3 program to play a three player, winner takes all glory game of Farkle

Your program will receive the state of the game, which contains:

>         index (where you sit at the table)
>         end_score (score required to win (20,000))
>         game_scores (all the players current score)
>         state_variable (space for you to put whatever you want)
> 
>         #round values, these change during the round
>         round_score (score of the current set of dice)
>         round_rollover (score from previous "hot streaks")
>         round_dice (current dice)
>         round_set_aside (dice you set aside before rolling)
>         round_used_in_score (lets you know which dice are adding to your score)

----------

Players should return an array showing which dice they want to set aside. This should be wrapped in a set_dice_aside(self) method

For instance, here's a player that will save dice that add to their score until the score they would get is 500 or greater

```python
class GoForFiveHundred(Bot):
    def set_dice_aside(self):
        while (self.round_score + self.round_rollover) < 500:
            return self.round_used_in_score
        return [True, True, True, True, True, True]
```


## Gameplay

The tournament runner can be found here: [Farkle_Fest_2K19](https://github.com/trbarron/Farkle_Fest_2K19). Run [`main.py`](https://github.com/trbarron/Farkle_Fest_2K19/blob/master/main.py) to run a tournament. I'll keep it updated with new submissions. Example programs can be found in [`farkle_bots.py`](https://github.com/trbarron/Farkle_Fest_2K19/blob/master/farkle_bots.py). Lots of code was lifted from [maxb](https://codegolf.stackexchange.com/users/79994/maxb), many thanks for that framework and code.

A tournament consists of 5000 games per 10 players (rounded up, so 14 players means 10,000 games). Each game will be three random players selected from the pool of players to fill the three positions. Players will not be able to be in the game twice. 

## Scoring

The winner of each game is the player with the most points at the end of the game. In the case of a tie at the end of a game all players with the maximum money amount are awarded a point. The player with the most points at the end of the tournament wins. I will post scores as I run the games.

The players submitted will be added to the pool. I added three dumb bots to start.

## Caveats

Do not modify the inputs. Do not attempt to affect the execution of any other program, except via cooperating or defecting. Do not make a sacrificial submission that attempts to recognize another submission and benefit that opponent at its own expense. [Standard loopholes](https://codegolf.meta.stackexchange.com/questions/1061/loopholes-that-are-forbidden-by-default) are banned.

Limit the time taken by your bot to be ~1s per turn. 

Submissions may not duplicate earlier submissions.

If you have any questions, feel free to ask.

## Winning

The competition will stay open indefinitely, as new submissions are posted. However, I will declare a winner (accept an answer) based on the results two month after this question was posted (November 2nd). 

Simulation of 5000 games between 5 bots completed in 675.7 seconds
	Each game lasted for an average of 15.987000 rounds
	8 games were tied between two or more bots
	0 games ran until the round limit, highest round was 48

	+----------------+----+--------+--------+------+------+-------+
	|Bot             |Win%|    Wins|  Played|   Max|   Avg|Avg win|
	+----------------+----+--------+--------+------+------+-------+
	|WaitBot         |95.6|    2894|    3028| 30500| 21988|  22365|
	|BruteForceOdds  |38.7|    1148|    2967| 25150| 15157|  20636|
	|GoForFiveHundred|19.0|     566|    2981| 24750| 12996|  20757|
	|GoForTwoGrand   |13.0|     390|    2997| 25450| 10879|  21352|
	|SetAsideAll     | 0.2|       6|    3027| 25200|  7044|  21325|
	+----------------+----+--------+--------+------+------+-------+

	+----------------+-------+-----+
	|Bot             |   Time|Time%|
	+----------------+-------+-----+
	|BruteForceOdds  |2912.70| 97.0|
	|WaitBot         |  58.12|  1.9|
	|GoForTwoGrand   |  13.85|  0.5|
	|GoForFiveHundred|  10.62|  0.4|
	|SetAsideAll     |   7.84|  0.3|
	+----------------+-------+-----+

And the results without WaitBot, which I'm still morally undecided on:

	+----------------+----+--------+--------+------+------+-------+
	|Bot             |Win%|    Wins|  Played|   Max|   Avg|Avg win|
	+----------------+----+--------+--------+------+------+-------+
	|BruteForceOdds  |72.0|    2698|    3748| 26600| 19522|  20675|
	|GoForFiveHundred|37.2|    1378|    3706| 25350| 17340|  20773|
	|GoForTwoGrand   |24.3|     927|    3813| 26400| 14143|  21326|
	|SetAsideAll     | 0.1|       5|    3733| 21200|  9338|  20620|
	+----------------+----+--------+--------+------+------+-------+
	+----------------+-------+-----+
	|Bot             |   Time|Time%|
	+----------------+-------+-----+
	|BruteForceOdds  |4792.26| 98.9|
	|GoForTwoGrand   |  24.53|  0.5|
	|GoForFiveHundred|  18.06|  0.4|
	|SetAsideAll     |  13.01|  0.3|
	+----------------+-------+-----+
