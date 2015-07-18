#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
from itertools import product
from NFA import NFA
from DFA import DFA
# Some small utils

class FiniteStateMachine:




    def getAlphabet(self):
        """
        Returns a set containing the alphabet.
        If the FSM is non-deterministic, this function does not return the epsilon symbol.
        """
        if type(self) == NFA:
            return self.alphabet - {self.EPSILON}
        return self.alphabet

    def get_transition_table(self):
        """
        Build a transition table for func, a function such [states] X [alphabet] -> [states]
        Returns a dictionnary of states where each element is a dictionnary with (key,value) = [alphabet],[states]
        """


        d = {}
        for x in sorted(self.states):
            d[x] = {}
            for c in self.alphabet:
                d[x][c] = self.delta(x, c)
                #        d[x].update(map(lambda c: (c,func(x, c)), alphabet.copy()))
        return d

    def accepted_words_under_max_length(self, max_length):
        """Try all words of length <=Prints the accepted words that"""
        accepted_words_list = []

        for x in range(1, max_length):
            for i in product(self.getAlphabet(), repeat=x): #IF NFA remove epsilon.
                entree = ''.join(i)
                if self.recognizes(entree):
                    accepted_words_list.append(entree)

        return accepted_words_list


    def accepted_words_under_word(self, max_word):
        """Try all words of before in the alphabetical enumeration and return the accepted words"""


        accepted_words_list = []
        for x in range(1, len(max_word) + 1):
            for i in product(self.getAlphabet(), repeat=x):
                entree = ''.join(i)
                if self.recognizes(entree):
                    accepted_words_list.append(entree)
                if entree == max_word:
                    break

        return accepted_words_list

#
#   To modify the FSM:
#

    def remap(self, q0, a, q):
        """
        This function changes the output of one transition
        q0 : the initial state
        a : a symbol of the alphabet
        q : the final states. Can be an object or a set of objects

        q0 -a-> set([q])
        """

        assert q0 in self.states
        assert a in self.alphabet
        assert q0 <= self.states

        table = self.get_transition_table()
        table[q0][a] = q

        self.delta = lambda x,c : table[x][c]


#
# Administrative functions:
#

    def pretty_print(self):
        """Displays all information about the NFA in an easy-to-read way. Not
        actually that easy to read if it has too many states.
        """
        print("")
        print("This NFA has %s states" % len(self.states))
        print("States:", self.states)
        print("Alphabet:", self.alphabet)
        print("Starting state:", self.start)
        print("Accepting states:", self.accepts)
        print("Transition function:")
        print("\t","\t".join(map(str, sorted(self.states))))
        for c in self.alphabet:
            results = map(lambda x: self.delta(x, c), sorted(self.states))
            print(c, "\t", "\t".join(map(str, results)))
        print("Current state:", self.current_state)
        print("Currently accepting:", self.status())
        print("")

    def pretty_print2(self):
        """Alternative print. Easier to read for DFA that are the result of the convertion of a NFA.
        """
        def str2(x):
            t = type(x)
            if t == set or t == frozenset or t == list:
                return '('+''.join([str(y)+", " for y in x])[:-2]+')'
            else : return str(x)

        print("")
        print("This NFA has %s states" % len(self.states))
        print("States:", map(str2,self.states))
        print("Alphabet:", self.alphabet)
        print("Starting state:", str2(self.start))
        print("Accepting states:", map(str2,self.accepts))
        print("Transition table:")

        tmp = "{"
        transition_table = self.get_transition_table()
        for x in sorted(self.states):
            tmp += str2(x)+":{"+", ".join([str(c)+":"+'{'+', '.join([str2(transition_table[x][c])])+'}' for c in self.alphabet])+"},\n"
           # tmp += str2(x)+":{"+", ".join([str(c)+":"+str2(transition_table[x][c]) for c in self.alphabet])+"},\n"
        tmp = tmp[:-2]+"}"

        print(tmp)

        print("Current state:", str2(self.current_state))
        print("Currently accepting:", self.status())
        print("")

#
# Simulating execution:
#



def save_machine(FA, path):
    "Saves a single automaton"

    FA = FA.copy()

    # Pickle cannot serialize lambda functions. We will instead serialize a transition table of the function.
    FA.delta = FA.get_transition_table()
    f = open(path, 'wb')
    p = pickle.Pickler(f, 2)
    p.dump(FA)
    print("Saved object at " + f.name)


def load_machine(path):
    """ Loads a single automaton """
    FA = pickle.load(open(path, 'rb'))
    d = FA.delta.copy()

    # Make the transition table a lambda function.
    FA.delta = lambda x, c: d[x][c]

    return FA


