import math
import random
import sys
import time
from numpy import cumsum

from collections import defaultdict
from multiprocessing import Pool
from os import path

ANSI = True
AUTO_FILE = 'internet.py'
LOCAL_FILE = 'farkle_bots.py'
DEBUG = False

def print_str(x, y, string):
    print("\033["+str(y)+";"+str(x)+"H"+string, end = "", flush = True)

class bcolors:
    WHITE = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

class Controller:

    def __init__(self, bots_per_game, games, bots, thread_id):
        """Initiates all fields relevant to the simulation

        Keyword arguments:
        bots_per_game -- the number of bots that should be included in a game
        games -- the number of games that should be simulated
        bots -- a list of all available bot classes
        """

        # global rules

        self.bots_per_game = bots_per_game
        self.games = games
        self.bots = bots
        self.number_of_bots = len(self.bots)
        self.wins = defaultdict(int)
        self.played_games = defaultdict(int)
        self.bot_timings = defaultdict(float)
        # self.wins = {bot.__name__: 0 for bot in self.bots}
        # self.played_games = {bot.__name__: 0 for bot in self.bots}
        self.end_score = 20000
        self.thresh_to_start = 0
        self.points_lost_if_farkle = -1000
        self.dice_using = 6
        self.thread_id = thread_id
        self.max_rounds = 200
        self.timed_out_games = 0
        self.tied_games = 0
        self.total_rounds = 0
        self.highest_round = 0
        #max, avg, avg_win, throws, success, rounds
        self.highscore = defaultdict(lambda:[0, 0, 0, 0, 0, 0])
        self.winning_scores = defaultdict(int)
        # self.highscore = {bot.__name__: [0, 0, 0] for bot in self.bots}

        #game values. stay persistent for the whole thing
        self.player_score = [0 for i in range(self.number_of_bots)]
        self.player_farkles_in_row = [0 for i in range(self.number_of_bots)]

        # Returns a fair dice throw

    def throw_dice(self,dice,set_aside):
        for d in range(self.dice_using):
            if not set_aside[d]: dice[d] = random.randint(1,6)
        return dice
        # Print the current game number without newline

    def score(self, dice, set_aside, rollover):
        """scores dice

        Keyword arguments:
        dice values -- the digits on the dice
        set_aside -- which had been set aside before. Helpful for figuring out if you farkled

        five = 50
        one = 100
        triple one = 1000
        triple 2 = 200
        triple 3 = 300
        triple 4 = 400
        triple 5 = 500
        triple 6 = 600
        one thru six = 1500
        three pairs = 1500
        two triplets = 2500
        four of a kind = 1000
        five of a kind = 2000
        six of a kind = 3000
        three farkles in a row = -1000

        returns if the score increased, current round score and which dice were involved in the score increasing
        """
        dice_used_in_scoring = [False for _ in range(self.dice_using)]
        score = 0

        #Check if there is a run
        if len(set(dice)) == 6:
            score_increased = True
            score = 1500
            dice_used_in_scoring = [True for di in range(self.dice_using)]

        pairs = 0
        triples = 0
        quads = 0
        pentas = 0
        hexas = 0
        for val in range(1,7):
            if dice.count(val) == 2:
                pairs += 1

            if dice.count(val) == 3:
                triples += 1
                for pa in range(self.dice_using):
                    if dice[pa] == val:
                        dice_used_in_scoring[pa] = True

            if dice.count(val) == 4:
                quads += 1
                score = 1000
                for pa in range(self.dice_using):
                    if dice[pa] == val:
                        dice_used_in_scoring[pa] = True

            if dice.count(val) == 5:
                pentas += 1
                score = 2000
                for pa in range(self.dice_using):
                    if dice[pa] == val:
                        dice_used_in_scoring[pa] = True

            if dice.count(val) == 6:
                hexas += 1
                score = 3000
                for pa in range(self.dice_using):
                    if dice[pa] == val:
                        dice_used_in_scoring[pa] = True

        if pairs == 3:
            score = 1500
            for pa in range(self.dice_using): dice_used_in_scoring[pa] = True

        if triples == 2:
            score = 2500

        if triples == 1:
            if dice.count(1) == 3: score = 100
            if dice.count(2) == 3: score = 200
            if dice.count(3) == 3: score = 300
            if dice.count(4) == 3: score = 400
            if dice.count(5) == 3: score = 500
            if dice.count(6) == 3: score = 600

        #add ones and fives
        for di in range(self.dice_using):
            if dice[di] == 1 and dice_used_in_scoring[di] == False:
                score += 100
                dice_used_in_scoring[di] = True
            if dice[di] == 5 and dice_used_in_scoring[di] == False:
                score += 50
                dice_used_in_scoring[di] = True

        #see if the score went up
        if sum(dice_used_in_scoring) > sum(set_aside): farkle = False
        else: farkle = True

        if sum(dice_used_in_scoring) == self.dice_using:
            #oh dang you have a hot streak. force a reroll
            set_aside = [False for _ in range(self.dice_using)]
            dice = self.throw_dice(dice,set_aside)
            farkle, score, new_rollover, dice_used_in_scoring,  = self.score(dice,set_aside, score)
            rollover += new_rollover
        return farkle, score, rollover, dice_used_in_scoring

    def print_progress(self, progress):
        length = 50
        filled = int(progress * length)
        fill = "=" * filled
        space = " " * (length - filled)
        perc = int(100 * progress)
        if ANSI:
            col = [
                bcolors.RED,
                bcolors.YELLOW,
                bcolors.WHITE,
                bcolors.BLUE,
                bcolors.GREEN
            ][int(progress * 4)]

            end = bcolors.ENDC
            print_str(5, 8 + self.thread_id,
                      "\t%s[%s%s] %3d%%%s" % (col, fill, space, perc, end)
                      )
        else:
            print(
                "\r\t[%s%s] %3d%%" % (fill, space, perc),
                flush=True,
                end=""
            )

        # Handles selecting bots for each game, and counting how many times
        # each bot has participated in a game

    def simulate_games(self):
        for game in range(self.games):
            if self.games > 100:
                if game % (self.games // 100) == 0 and not DEBUG:
                    if self.thread_id == 0 or ANSI:
                        progress = (game + 1) / self.games
                        self.print_progress(progress)
            game_bot_indices = random.sample(
                range(self.number_of_bots),
                self.bots_per_game
            )

            game_bots = [None for _ in range(self.bots_per_game)]
            for i, bot_index in enumerate(game_bot_indices):
                self.played_games[self.bots[bot_index].__name__] += 1
                game_bots[i] = self.bots[bot_index](i, self.end_score)

            self.play(game_bots)
        if not DEBUG and (ANSI or self.thread_id == 0):
            self.print_progress(1)

        self.collect_results()

    def play(self, game_bots):
        """Simulates a single game between the bots present in game_bots

        Keyword arguments:
        game_bots -- A list of instantiated bot objects for the game
        """
        last_round = False
        last_round_initiator = -1
        round_number = 0
        game_scores = [0 for _ in range(self.bots_per_game)]

        # continue until one bot has reached end_score points
        while not last_round:
            for index, bot in enumerate(game_bots):
                t0 = time.clock()
                self.single_bot(index, bot, game_scores, last_round)
                t1 = time.clock()
                self.bot_timings[bot.__class__.__name__] += t1 - t0

                if game_scores[index] >= self.end_score and not last_round:
                    last_round = True
                    last_round_initiator = index
            round_number += 1

            # maximum of 200 rounds per game
            if round_number > self.max_rounds - 1:
                last_round = True
                self.timed_out_games += 1
                # this ensures that everyone gets their last turn
                last_round_initiator = self.bots_per_game

        # make sure that all bots get their last round
        for index, bot in enumerate(game_bots[:last_round_initiator]):
            t0 = time.clock()
            self.single_bot(index, bot, game_scores, last_round)
            t1 = time.clock()
            self.bot_timings[bot.__class__.__name__] += t1 - t0

        # calculate which bots have the highest score
        max_score = max(game_scores)
        nr_of_winners = 0
        for i in range(self.bots_per_game):
            bot_name = game_bots[i].__class__.__name__
            # average score per bot
            self.highscore[bot_name][1] += game_scores[i]
            if self.highscore[bot_name][0] < game_scores[i]:
                # maximum score per bot
                self.highscore[bot_name][0] = game_scores[i]
            if game_scores[i] == max_score:
                # average winning score per bot
                self.highscore[bot_name][2] += game_scores[i]
                nr_of_winners += 1
                self.wins[bot_name] += 1
        if nr_of_winners > 1:
            self.tied_games += 1
        self.total_rounds += round_number
        self.highest_round = max(self.highest_round, round_number)
        self.winning_scores[max_score] += 1

    def single_bot(self, index, bot, game_scores, last_round):
        """Simulates a single round for one bot

        Keyword arguments:
        index -- The player index of the bot (e.g. 0 if the bot goes first)
        bot -- The bot object about to be simulated
        game_scores -- A list of ints containing the scores of all players
        last_round -- Boolean describing whether it is currently the last round

        """

        dice = [0 for i in range(self.dice_using)]
        set_aside = [False for i in range(self.dice_using)]
        dice = self.throw_dice(dice,set_aside)
        round_rollover = 0

        farkle,round_score, round_rollover, used_in_score = self.score(dice,set_aside,round_rollover)

        while not farkle and min(set_aside) == False:
            farkle,round_score, round_rollover, used_in_score = self.score(dice,set_aside, round_rollover)
            bot.update_state(round_score, round_rollover, dice,set_aside,used_in_score)

            if DEBUG:
                desc = "%d: Bot %24s has dice %20s with " + \
                       "scores %5s and rollover %5s. Set aside: %40s. last round == %5s. Farkle == %5s."
                if ANSI: print(bcolors.BLUE + desc % (index, bot.__class__.__name__,
                              dice, round_score, round_rollover, set_aside, last_round, farkle))
                else: print(desc % (index, bot.__class__.__name__,
                              dice, round_score, round_rollover, set_aside, last_round, farkle))

            set_aside = bot.set_dice_aside()
            dice = self.throw_dice(dice,set_aside)

        #if you hotstreaked you'll have rollover, add that in now

        #if you farkled, you get zero
        if farkle:
            round_score = 0
            self.player_farkles_in_row[index] += 1
            #if you farkle three times it takes away a thousand points
            if self.player_farkles_in_row[index] == 3:
                round_score = -1000
                self.player_farkles_in_row[index] = 0
        else:
            farkle, round_score, round_rollover, round_used_in_score = self.score(dice,set_aside,round_rollover)
            round_score += round_rollover

        #first score requires going over the thresh_to_start
        if game_scores[index] != 0 or round_score >= self.thresh_to_start:
            game_scores[index] += round_score

        if DEBUG:
            desc = "%d: Bot %24s gets %5s " + \
                   "total scores %15s and last round == %5s"
            if ANSI: print(bcolors.ENDC + desc % (index, bot.__class__.__name__,
                          round_score, game_scores, last_round))
            else: print(desc % (index, bot.__class__.__name__,
                          round_score, game_scores, last_round))
        bot_name = bot.__class__.__name__
        # average throws per round
        self.highscore[bot_name][3] += round_score
        # average success rate per round
        self.highscore[bot_name][4] += round_score
        # total number of rounds
        self.highscore[bot_name][5] += 1

    def collect_results(self):
        self.bot_stats = {
            bot.__name__: [
                self.wins[bot.__name__],
                self.played_games[bot.__name__],
                self.highscore[bot.__name__]
            ]
        for bot in self.bots}

def print_results(total_bot_stats, total_game_stats, elapsed_time):
    """Print the high score after the simulation

    Keyword arguments:
    total_bot_stats -- A list containing the winning stats for each thread
    total_game_stats -- A list containing controller stats for each thread
    elapsed_time -- The number of seconds that it took to run the simulation
    """

    # Find the name of each bot, the number of wins, the number
    # of played games, and the win percentage
    wins = defaultdict(int)
    played_games = defaultdict(int)
    highscores = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    bots = set()
    timed_out_games = sum(s[0] for s in total_game_stats)
    tied_games = sum(s[1] for s in total_game_stats)
    total_games = sum(s[2] for s in total_game_stats)
    total_rounds = sum(s[4] for s in total_game_stats)
    highest_round = max(s[5] for s in total_game_stats)
    average_rounds = total_rounds / total_games
    winning_scores = defaultdict(int)
    bot_timings = defaultdict(float)

    for stats in total_game_stats:
        for score, count in stats[6].items():
            winning_scores[score] += count

    for thread in total_bot_stats:
        for bot, stats in thread.items():
            wins[bot] += stats[0]
            played_games[bot] += stats[1]

            highscores[bot][0] = max(highscores[bot][0], stats[2][0])
            for i in range(1, 6):
                highscores[bot][i] += stats[2][i]
            bots.add(bot)

    for bot in bots:
        bot_timings[bot] += sum(s[3][bot] for s in total_game_stats)

    bot_stats = [[bot, wins[bot], played_games[bot], 0] for bot in bots]

    for i, bot in enumerate(bot_stats):
        bot[3] = 100 * bot[1] / bot[2] if bot[2] > 0 else 0
        bot_stats[i] = tuple(bot)

    # Sort the bots by their winning percentage
    sorted_scores = sorted(bot_stats, key=lambda x: x[3], reverse=True)
    # Find the longest class name for any bot
    max_len = max([len(b[0]) for b in bot_stats])

    # Print the highscore list
    if ANSI:
        print_str(0, 9 + threads, "")
    else:
        print("\n")

    sim_msg = "\nSimulation of %d games between %d bots " + \
              "completed in %.1f seconds"
    print(sim_msg % (total_games, len(bots), elapsed_time))
    print("\tEach game lasted for an average of %f rounds" % average_rounds)
    print("\t%d games were tied between two or more bots" % tied_games)
    print("\t%d games ran until the round limit, highest round was %d\n"
          % (timed_out_games, highest_round))

    print_bot_stats(sorted_scores, max_len, highscores)
    print_time_stats(bot_timings, max_len)

def print_bot_stats(sorted_scores, max_len, highscores):
    """Print the stats for the bots

    Keyword arguments:
    sorted_scores -- A list containing the bots in sorted order
    max_len -- The maximum name length for all bots
    highscores -- A dict with additional stats for each bot
    """
    delimiter_format = "\t+%s%s+%s+%s+%s+%s+%s+%s+%s+%s+"
    delimiter_args = ("-" * (max_len), "", "-" * 4, "-" * 8,
                      "-" * 8, "-" * 6, "-" * 6, "-" * 7, "-" * 6, "-" * 8)
    delimiter_str = delimiter_format % delimiter_args
    print(delimiter_str)
    print("\t|%s%s|%4s|%8s|%8s|%6s|%6s|%7s|"
          % ("Bot", " " * (max_len - 3), "Win%", "Wins",
             "Played", "Max", "Avg", "Avg win"))
    print(delimiter_str)

    for bot, wins, played, score in sorted_scores:
        highscore = highscores[bot]
        bot_max_score = highscore[0]
        bot_avg_score = highscore[1] / played
        bot_avg_win_score = highscore[2] / max(1, wins)
        bot_avg_throws = highscore[3] / highscore[5]
        bot_success_rate = 100 * highscore[4] / highscore[5]

        space_fill = " " * (max_len - len(bot))
        format_str = "\t|%s%s|%4.1f|%8d|%8d|%6d|%6.0f|%7.0f|%6.0f|%8.0f|"
        format_arguments = (bot, space_fill, score, wins,
                            played, bot_max_score, bot_avg_score,
                            bot_avg_win_score, bot_avg_throws, bot_success_rate)
        print(format_str % format_arguments)

    print(delimiter_str)
    print()

def print_time_stats(bot_timings, max_len):
    """Print the execution time for all bots

    Keyword arguments:
    bot_timings -- A dict containing information about timings for each bot
    max_len -- The maximum name length for all bots
    """
    total_time = sum(bot_timings.values())
    sorted_times = sorted(bot_timings.items(),
                          key=lambda x: x[1], reverse=True)

    delimiter_format = "\t+%s+%s+%s+"
    delimiter_args = ("-" * (max_len), "-" * 7, "-" * 5)
    delimiter_str = delimiter_format % delimiter_args
    print(delimiter_str)

    print("\t|%s%s|%7s|%5s|" % ("Bot", " " * (max_len - 3), "Time", "Time%"))
    print(delimiter_str)
    for bot, bot_time in sorted_times:
        space_fill = " " * (max_len - len(bot))
        perc = 100 * bot_time / total_time
        print("\t|%s%s|%7.2f|%5.1f|" % (bot, space_fill, bot_time, perc))
    print(delimiter_str)
    print()

def run_simulation(thread_id, bots_per_game, games_per_thread, bots):
    """Used by multithreading to run the simulation in parallel

    Keyword arguments:
    thread_id -- A unique identifier for each thread, starting at 0
    bots_per_game -- How many bots should participate in each game
    games_per_thread -- The number of games to be simulated
    bots -- A list of all bot classes available
    """
    try:
        controller = Controller(bots_per_game,
            games_per_thread, bots, thread_id)
        controller.simulate_games()
        controller_stats = (
            controller.timed_out_games,
            controller.tied_games,
            controller.games,
            controller.bot_timings,
            controller.total_rounds,
            controller.highest_round,
            controller.winning_scores
        )
        return (controller.bot_stats, controller_stats)
    except KeyboardInterrupt:
        return {}

if __name__ == "__main__":

    games = 1000
    bots_per_game = 3
    threads = 1

    if ANSI:
        print(chr(27) + "[2J", flush =  True)
        print_str(1,3,"")
    else:
        print()

    if path.isfile(AUTO_FILE):
        exec('from %s import *' % AUTO_FILE[:-3])
    else:
        exec('from %s import *' % LOCAL_FILE[:-3])

    bots = get_all_bots()

    if bots_per_game > len(bots):
        print("\tRequested too many bots... using the num you have")
        bots_per_game = len(bots)
    if bots_per_game < 2:
        print("\tAt least 2 bots per game is needed")
        bots_per_game = 2
    if games <= 0:
        print("\tAt least 1 game is needed")
        games = 1
    if threads <= 0:
        print("\tAt least 1 thread is needed")
        threads = 1
    if DEBUG:
        print("\tRunning in debug mode, with 1 thread and 1 game")
        threads = 1
        games = 1

    games_per_thread = math.ceil(games / threads)

    print("\tStarting simulation with %d bots" % len(bots))
    sim_str = "\tSimulating %d games with %d bots per game"
    print(sim_str % (games, bots_per_game))
    print("\tRunning simulation on %d threads" % threads)
    if len(sys.argv) == 1:
        print("\tFor help running the script, use the -h flag")
    print()

    with Pool(threads) as pool:
        t0 = time.time()
        results = pool.starmap(
            run_simulation,
            [(i, bots_per_game, games_per_thread, bots) for i in range(threads)]
        )
        t1 = time.time()

        if not DEBUG:
            total_bot_stats = [r[0] for r in results]
            total_game_stats = [r[1] for r in results]
            print_results(total_bot_stats, total_game_stats, t1-t0)