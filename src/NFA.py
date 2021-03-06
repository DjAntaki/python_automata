from FiniteStateMachine import FiniteStateMachine
from DFA import DFA


class NFA(FiniteStateMachine):
    """This class represents a non-deterministic finite automaton."""

    def __init__(self, states, alphabet, delta, start, accepts, epsilon='epi'):
        """
        The inputs to the class are as follows :
        * states: An iterable containing the states of the NFA. States must be immutable. None is not a valid state.
        * alphabet: An iterable containing the symbols in the DFA's alphabet. Symbols must be immutable. No need to put epsilon in the alphabet.
        * delta: A complete function from [states]x[alphabets]->{None | [states] | set([states])}.
        * start: The state at which the NFA begins operation. Multiple initial states are supported.
        * accepts: A list containing the "accepting" or "final" states of the NFA.
        * epsilon : a immutable representing the epsilon transitions symbol

        Making delta a function rather than a transition table makes it much easier to define certain NFAs.
        If you want to use a transition table, you can just do this:
         delta = lambda q,c: set(transition_table[q][c])

        Finally, the names of states and inputs should be hashable. This generally means strings, numbers,
        or tuples of hashables.
        """

        self.states = set(states)

        if start in states:
            self.start = {start}
        else :
            assert start <= states
            self.start = set(start)

        self.delta = delta
        self.accepts = set(accepts)
        self.alphabet = set(alphabet)
        self.current_state = self.start.copy()
        self.EPSILON=epsilon
        self.alphabet.add(self.EPSILON)
        self._epsilon_closure()
        self.validate()

#        if len(self.start) is not 1:
 #           warnings.warn("Your NFA has more than one initial state. ")

    def validate(self):
        """Checks that:
        (1) The accepting-state set is a subset of the state set.
        (2) The start-state is a member of the state set.
        (3) The current-state is a member of the state set.
        (4) Every transition returns a set of members of the state set.
        """
        assert not None in self.states
        assert set(self.accepts).issubset(set(self.states))
        assert self.start <= self.states
        assert self.current_state <= self.states
        for state in self.states:
            for char in self.alphabet:
                a = self.delta(state,char)
                if type(a) == list or type(a) == set:
                    assert a <= self.states
                elif not a is None:
                    assert a in self.states

    def copy(self):
        """Returns a copy of the NFA. No data is shared with the original."""
        return NFA(self.states, self.alphabet, self.delta, self.start, self.accepts, self.EPSILON)

#
# Simulating execution:
#
    def step(self, char):
        """Updates the NFA's current state(s) based on a single character of input."""

        self.current_state = self.input(char)

        self._epsilon_closure()

    def input(self, char):
        """Calculate the states resulting on a single character of input based on current state. This function does not change self.current_state. """
        a = set()
        q = [self.delta(i,char) for i in self.current_state]

        for x in q:
            if type(x) == set or type(x) == list:
                a.update(x)
            elif x is not None :
                a.add(x)
        return a



    def _epsilon_closure(self):
        """Update the NFA's current state based on all epsilon transition you can take from any member of current_state"""
        s = len(self.current_state)
        while True:
            self.current_state.update(self.input(self.EPSILON))
            x = len(self.current_state)
            if x == s :
                break
            else :
                s = x

    def input_sequence(self, char_sequence, verbose = False):
        """Updates the NFA's current state based on an iterable of inputs."""
        if char_sequence != self.EPSILON:

            if verbose:
                print('Starting state : '+str(self.current_state))
            for char in char_sequence:
                if char not in self.alphabet:
                    if verbose:
                        print('Character '+str(char)+' not in alphabet')
                    self.current_state = set()
                    return
                self.step(char)
                if (verbose):
                    print('input : '+ str(char))
                    print('state(s) : '+str(self.current_state))

    def status(self):
        """Indicates whether one of the NFA's current state is accepting."""
        return any([i in self.accepts for i in self.current_state])

    def reset(self):
        """Returns the NFA to the starting state."""
        self.current_state = self.start.copy()
        self._epsilon_closure()

    def recognizes(self, char_sequence, verbose = False):
        """Indicates whether the NFA accepts a given string."""
        state_save = self.current_state
        self.reset()
        self.input_sequence(char_sequence, verbose)
        valid = self.status()
        self.current_state = state_save
        return valid

    def toDFA(self):
        """
        Returns an unminimized DFA that accepts the same language as th NFA instance.
        """
        saved_state = self.current_state
        self.reset()
        delta = {}
        dfa_states = []
        alpha = self.alphabet.copy()
        alpha.remove(self.EPSILON)
        to_explore_queue = [frozenset(self.current_state)]
        while(len(to_explore_queue) != 0):
            e = to_explore_queue.pop(0)
            delta[e] = dict()
            for a in alpha :
                self.current_state = e
                self.step(a)
                entry = frozenset(self.current_state)
                delta[e][a] = entry
                if entry not in to_explore_queue and entry not in dfa_states:
                    to_explore_queue.append(entry)
            dfa_states.append(e)

        #   Calculate accept
        accept = filter(lambda x: len(self.accepts & x ) > 0,dfa_states)
        self.current_state = saved_state
        return DFA(dfa_states, alpha, lambda x,y : delta[x][y], dfa_states[0], accept)

