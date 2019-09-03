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