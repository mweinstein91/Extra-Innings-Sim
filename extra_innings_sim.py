#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 19:29:24 2018

@author: Mark
"""


class extra_innings():

    # Constructor for an extra innings class
    def __init__(self, second_base_start):

        # holds the event of the last plate appearance
        self.last_PA = 'None'
        self.inning = 10
        self.inning_half = 'Top'
        # decides on the initial base state given the parameter
        if (second_base_start == 10):
            self.base_state = [0, 1, 0]
        else:
            self.base_state = [0, 0, 0]
        self.outs = 0
        self.score_home = 0
        self.score_away = 0
        # each event with the amount it moves the bases
        self.events = {"1B": 1, "2B": 2, "3B": 3, "HR": 0, "BB": 1, "GD": 0, "FLY": 0, "SO": 0}

        # smoothed probability of each event above
        self.weights = [.14, .05, .004, .03, .085, .24, .23, .221]

        self.runner_start = second_base_start

    # checks if a team has won
    def check_winner(self):
        return ((
                            self.score_home < self.score_away and self.outs == 3 and self.inning_half == 'Bottom') or self.check_walkoff())

    # randomly selects an event from our dictionary of events
    def sim_event(self):
        import numpy as np
        self.last_PA = str(np.random.choice(list(self.events.keys()), 1, p=self.weights)[0])
        return (self.last_PA)

    # simulates a PA. sims an event, updates the base out state and score
    def sim_PA(self):
        pa_result = self.sim_event()
        runs = self.update_base_out_state(pa_result)
        self.place_hitter(pa_result)
        if (runs > 0):
            self.update_score(runs)

    # simulates a half inning
    def sim_half_inning(self):
        while not self.check_inning_end():
            self.sim_PA()

    # resets for the internal state for a half of an inning
    def iterate_inning_half(self):
        if (self.inning_half == 'Bottom'):
            self.inning_half = 'Top'
            self.inning += 1
        elif (self.inning_half == 'Top'):
            self.inning_half = 'Bottom'
        self.outs = 0
        if (self.inning >= self.runner_start):
            self.base_state = [0, 1, 0]
        else:
            self.base_state = [0, 0, 0]

    # checks if the inning should end
    def check_inning_end(self):
        return (self.outs >= 3 or self.check_walkoff())

    # advances all runners by one base (assumption)
    def advance_runners(self):
        scored = self.base_state[2]
        self.base_state[2] = self.base_state[1]
        self.base_state[1] = self.base_state[0]
        self.base_state[0] = 0
        return (scored)

    def check_walkoff(self):
        # check to see if the game ends early because of a walk off
        return (self.inning_half == "Bottom" and self.score_home > self.score_away)

    # checks if bases are empty
    def is_empty(self):
        return (self.base_state == [0, 0, 0])

    # places hittter at correct spot on base path based on the event
    def place_hitter(self, event):
        if (self.events[event] > 0):
            self.base_state[self.events[event] - 1] = 1

    # updates the score for a given amount of runs scored
    def update_score(self, runs):
        if (self.inning_half == 'Top'):
            self.score_away += runs
        else:
            self.score_home += runs

    # updates the base_state by incrementing runners one at a time. Calculates and returns total runs scored.
    def update_base_out_state(self, event):
        import numpy as np
        # rules for GD, FLY, SO
        if (self.events[event] == 0 and event != "HR" and event != 'FLY'):
            self.outs += 1
            return 0
        # Handles HR
        elif (event == "HR"):
            runs_scored = sum(self.base_state) + 1
            self.base_state = [0, 0, 0]
            return runs_scored
        # Handles difference between BB and single
        elif (event == "BB" and self.base_state[0] == 0):
            return 0
        elif (event == "FLY" and self.outs < 2):
            self.outs += 1
            return (self.advance_runners())
        else:
            # Handles other cases
            return sum([self.advance_runners() for i in range(self.events[event])])

    # simulates extra_innings
    def sim_extra_innings(self):
        while (not self.check_winner()):
            self.sim_half_inning()
            if (not self.check_winner()):
                self.iterate_inning_half()
        return {"Inning": self.inning, "home_score": self.score_home, "away_score": self.score_away}

    # prints internal state
    def display_state(self):
        print("Home score: {}".format(self.score_home) + " Away score: {}".format(self.score_away)
              + " Outs: {}".format(self.outs) + " Men On Base:{}".format(self.base_state)
              + " Inning: {}".format(self.inning) + " Half:{}".format(self.inning_half) + " Last PA:{}".format(
                    self.last_PA))


# simulate using class, inning 100000 represents never putting a runner on base.
# Prints inning and percent of games that reach 13 innings plus
import pandas as pd

iterate = [100000, 10, 11, 12]
innings = []
for i in iterate:
    for j in range(10000):
        new_game = extra_innings(i)
        innings.append(new_game.sim_extra_innings())
        j += 1
    innings_df = pd.DataFrame(innings)
    print("Inning: {}: ".format(i) + str(len(innings_df[innings_df.Inning >= 13]) / len(innings_df)))