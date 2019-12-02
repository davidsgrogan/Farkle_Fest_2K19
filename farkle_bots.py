# Returns a list of all bot classes which inherit from the Bot class
def get_all_bots():
    return Bot.__subclasses__()

# The parent class for all bots
class Bot:

    def __init__(self, index, end_score):
        self.index = index
        self.end_score = end_score
        self.state_variable = None

        #dummy values, these change during the round
        self.round_score = 0
        self.round_rollover = 0
        self.round_dice = []
        self.round_set_aside = []
        self.round_used_in_score = [False,False,False,False,False,False]

    def update_state(self, round_score,round_rollover,round_dice,round_set_aside,round_used_in_score,game_scores):
        self.round_score = round_score
        self.round_rollover = round_rollover
        self.round_dice = round_dice
        self.round_set_aside = round_set_aside
        self.round_used_in_score = round_used_in_score
        self.game_scores = game_scores


    def set_dice_aside(self):
        return [True,True,True,True,True,True]

class SetAsideAll(Bot):
    def set_dice_aside(self):
        return [True,True,True,True,True,True]

class GoForFiveHundred(Bot):
    def set_dice_aside(self):
        while (self.round_score + self.round_rollover) < 500:
            return self.round_used_in_score
        return [True, True, True, True, True, True]

class GoForTwoGrand(Bot):
    def set_dice_aside(self):
        while (self.round_score + self.round_rollover) < 2000:
            return self.round_used_in_score
        return [True,True,True,True,True,True]
from main import Controller
from farkle_bots import Bot

scoreDevice = Controller(1, 1, [], 0)

class BruteForceOdds(Bot):
    def set_dice_aside(self):
        stop_score = self.round_score + self.round_rollover
        if self.game_scores[self.index] + stop_score > max(self.game_scores + [self.end_score]):
            # Take the win
            return [True, True, True, True, True, True]

        using = self.round_used_in_score[:]
        if self.round_dice.count(5) < 3:
            for i in range(len(using)):
                if self.round_dice[i] == 5 and not self.round_set_aside[i] and using.count(True) > self.round_set_aside.count(True)+1:
                    using[i] = False
        if self.round_dice.count(1) < 3:
            for i in range(len(using)):
                if self.round_dice[i] == 1 and not self.round_set_aside[i] and using.count(True) > self.round_set_aside.count(True)+1:
                    using[i] = False
        if using.count(True) < 3 and self.round_rollover == 0:
            # Stopping here is basically never a good idea
            return using

        if bruteScore(self.round_dice, using, self.round_rollover) > stop_score:
            return using
        return [True, True, True, True, True, True]

def bruteScore(round_dice, set_aside, base_score):
    base_dice = []
    for i in range(len(round_dice)):
        if(set_aside[i]):
            base_dice.append(round_dice[i])
    totalCount = 0
    totalScore = 0
    for new_dice in allPossibleRolls(len(round_dice) - len(base_dice)):
        dice = base_dice + new_dice
        keep = [True]*len(base_dice)+[False]*len(new_dice)
        farkle, round_score, round_rollover, used_in_score = scoreDevice.score(dice, keep, base_score)
        totalCount += 1
        if not farkle:
            totalScore += round_score + round_rollover
    return totalScore / totalCount

def allPossibleRolls(length):
    if length == 0:
        yield []
        return
    for i in range(1,7):
        for l in allPossibleRolls(length-1):
            yield [i]+l