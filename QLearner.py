""""""
"""
Template for implementing QLearner  (c) 2015 Tucker Balch

Copyright 2018, Georgia Institute of Technology (Georgia Tech)
Atlanta, Georgia 30332
All Rights Reserved

Template code for CS 4646/7646

Georgia Tech asserts copyright ownership of this template and all derivative
works, including solutions to the projects assigned in this course. Students
and other users of this template code are advised not to share it with others
or to make it available on publicly viewable websites including repositories
such as github and gitlab.  This copyright statement should not be removed
or edited.

We do grant permission to share solutions privately with non-students such
as potential employers. However, sharing with other current or future
students of CS 7646 is prohibited and subject to being investigated as a
GT honor code violation.

-----do not edit anything above this line---

Student Name: Tucker Balch (replace with your name)
GT User ID: tb34 (replace with your User ID)
GT ID: 900897987 (replace with your GT ID)
"""

import json

import random as rand

import numpy as np


class QLearner(object):

    def author(self):
        return 'ytsai36'

    """
    This is a Q learner object.

    :param num_states: The number of states to consider.
    :type num_states: int
    :param num_actions: The number of actions available..
    :type num_actions: int
    :param alpha: The learning rate used in the update rule. Should range between 0.0 and 1.0 with 0.2 as a typical value.
    :type alpha: float
    :param gamma: The discount rate used in the update rule. Should range between 0.0 and 1.0 with 0.9 as a typical value.
    :type gamma: float
    :param rar: Random action rate: the probability of selecting a random action at each step. Should range between 0.0 (no random actions) to 1.0 (always random action) with 0.5 as a typical value.
    :type rar: float
    :param radr: Random action decay rate, after each update, rar = rar * radr. Ranges between 0.0 (immediate decay to 0) and 1.0 (no decay). Typically 0.99.
    :type radr: float
    :param dyna: The number of dyna updates for each regular update. When Dyna is used, 200 is a typical value.
    :type dyna: int
    :param verbose: If “verbose” is True, your code can print out information for debugging.
    :type verbose: bool
    """
    def __init__(
        self,
        num_states=100,
        num_actions=4,
        alpha=0.2,
        gamma=0.9,
        rar=0.5,
        radr=0.99,
        dyna=0,
        verbose=False,
    ):
        """
        Constructor method
        """
        self.verbose = verbose
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0
        self.Q = np.zeros((num_states, num_actions))
        # Dyna-Q parameters
        self.exp_s = []
        self.exp_a = []
        self.exp_s_prime = []
        self.exp_r = []

    def load(self, Q):
        # Load Q table
        self.Q = np.array(Q)

    def dump(self):
        # dump Q table as json string
        return json.dumps(self.Q.tolist())

    def querysetstate(self, s):
        """
        Update the state without updating the Q-table

        :param s: The new state
        :type s: int
        :return: The selected action
        :rtype: int
        """
        # This function usaully used for setting initial state and action
        action = self.__choose_next_action(s, decay=False)
        if self.verbose:
            print(f"s = {s}, a = {action}")
        # Saved the new state
        self.s = s
        self.a = action
        return action

    def query(self, s_prime, r):
        """
        Update the Q table and return an action

        :param s_prime: The new state
        :type s_prime: int
        :param r: The immediate reward
        :type r: float
        :return: The selected action
        :rtype: int
        """

        # First, update the Q table and get a_prime
        self.__update_Q_table(self.s, self.a, s_prime, r)
        self.__update_exp(self.s, self.a, s_prime, r)

        # Run Dyna to bosst learning if needed
        if self.dyna > 0:
            self.__run_dyna(self.s, self.a, s_prime, r)

        # Choose next action and decaly the probability
        action = self.__choose_next_action(s_prime, decay=True)

        if self.verbose:
            print(f"s = {s_prime}, a = {action}, r={r}")

        # Saved the new state
        self.s = s_prime
        self.a = action
        return action

    def __update_exp(self, s, a, s_prime, r):
        # Memorize (s, a) for Dyna-Q
        self.exp_s.append(s)
        self.exp_a.append(a)
        self.exp_s_prime.append(s_prime)
        self.exp_r.append(r)

    def __update_Q_table(self, s, a, s_prime, r):
        """
        Update the Q table using the formula
        """
        # Fist component is update from past experience
        # Second component is update from imporved estimate from new state
        # which is immediate reward + discounted rate * future reward
        self.Q[s, a] = (1 - self.alpha) * self.Q[s, a] + self.alpha * (r + self.gamma * self.Q[s_prime, np.argmax(self.Q[s_prime])])

    def __choose_next_action(self, s_prime, decay=False):
        # Random select an action or find the optimal one
        prob = rand.uniform(0.0, 1.0)
        if prob <= self.rar:
            action = rand.randint(0, self.num_actions - 1)
        else:
            action = np.argmax(self.Q[s_prime])
        # Decay the random probability
        if decay:
            self.rar *= self.radr
        return action

    def __run_dyna(self, s, a, s_prime, r):
        """
        Run Dyna-Q algorithm to boost learning
        """
        # We halucinate experience by random simluation
        # Finally, we update Q table accordingly

        # Halucinate experience and update Q table
        # We should random select the (s, a) combination we seen before
        rand_i = np.random.randint(0, len(self.exp_s), size=self.dyna)
        for i in rand_i:
            new_s = self.exp_s[i]
            new_a = self.exp_a[i]
            new_s_prime = self.exp_s_prime[i]
            new_r = self.exp_r[i]
            self.__update_Q_table(int(new_s), int(new_a), int(new_s_prime), new_r)


if __name__ == "__main__":
    print("Remember Q from Star Trek? Well, this isn't him")
