#!/usr/bin/env python3
from collections import namedtuple
from itertools import chain
from operator import itemgetter
from random import choice
import sys

LIAR = 'liar'

nominals = list([str(i) for i in range(1, 6)])
dice_values = nominals + ['*']

SimulationState = namedtuple('SimulationState', 'dices whos_turn last_action')


def concat(list_of_lists, ret_type=list):
    return ret_type(chain(*list_of_lists))


def create_triple(index):
    """
    >>> create_triple(0)
    ['11', '12', '13', '14', '15', '1*', '21', '22', '23', '24', '25']
    >>> create_triple(5)
    ['111', '112', '113', '114', '115', '6*', '121', '122', '123', '124', '125']"""
    return [str(index * 2 + 1) + n for n in nominals] + \
           [str(index + 1) + '*'] + \
           [str(index * 2 + 2) + n for n in nominals]

#bets = concat(create_triple(i) for i in range(10)) + ['liar']
bets = create_triple(0) + ['2*'] + ['liar']
#print(bets)


def simulate_once(ss) -> 'True if we won':
    next_turn = make_random_action(ss.last_action)
    if (next_turn == LIAR) or (not is_possible(ss)):
        return determine_winner(ss) == 0
    return simulate_once(SimulationState(ss.dices, next_player(ss.whos_turn), next_turn))


def next_player(player_id):
    """
    >>> next_player(0)
    1
    >>> next_player(1)
    0"""
    return (player_id + 1) % 2


def determine_winner(ss):
    """Return index of a winner
    >>> determine_winner(SimulationState(['1', '1'], 0, '12'))
    0
    >>> determine_winner(SimulationState(['1', '*'], 1, '11'))
    0
    >>> determine_winner(SimulationState(['4', '*'], 0, '24'))
    1
    >>> determine_winner(SimulationState(['*', '4'], 1, '25'))
    1
    >>> determine_winner(SimulationState(['*', '4'], 0, '2*'))
    0"""
    if len([d for d in ss.dices if d in ['*', ss.last_action[1]]]) >= int(ss.last_action[:-1]):
        return next_player(ss.whos_turn)
    else:
        return ss.whos_turn


def all_possible_actions(for_action):
    """
    >>> all_possible_actions('25')
    ['2*', 'liar']
    >>> all_possible_actions('1*')
    ['21', '22', '23', '24', '25', '2*', 'liar']
    >>> len(all_possible_actions(None)) == len(bets) - 1
    True
    >>> len(all_possible_actions('')) == len(bets) - 1
    True"""
    if not for_action:
        return bets[:-1]
    return bets[bets.index(for_action) + 1:]


def make_random_action(last_action):
    actions = all_possible_actions(last_action)
    if (actions[-1] == LIAR) and (len(actions) > 1):
        return choice([LIAR, choice(actions[:-1])])
    return choice(actions)


def is_possible(ss):
    """
    >>> is_possible(SimulationState(['3', '4'], 0, '23'))
    True
    >>> is_possible(SimulationState(['1', '*'], 0, '22'))
    False
    >>> is_possible(SimulationState(['1', '*'], 0, '12'))
    True
    >>> is_possible(SimulationState(['*', '3'], 1, '12'))
    True
    >>> is_possible(SimulationState(['*', '4'], 0, '25'))
    True"""
    dice_of_current_player = ss.dices[ss.whos_turn]
    if (not ss.last_action) or (ss.last_action[0] == '1') or (dice_of_current_player == '*'):
        return True
    return dice_of_current_player == ss.last_action[1]


def random_dice():
    return choice(dice_values)


def simulate(ss, last_move='', n=100):
    if ss.last_action == LIAR:
        return sum(determine_winner(SimulationState([ss.dices[0], d], 0, last_move)) == 0 for d in dice_values) / \
               len(dice_values)
    return sum(simulate_once(SimulationState([ss.dices[0], random_dice()], 1, ss.last_action)) for i in range(n)) / n


def decide(my_dice, last_move):
    if not last_move:
        return '1' + my_dice
    d = {b: simulate(SimulationState([my_dice, ''], 0, b), last_move, n=100) for b in all_possible_actions(last_move)}
    return max(d.items(), key=itemgetter(1))[0]


if __name__ == '__main__':
    import doctest
    doctest.testmod()


    line = sys.stdin.readline()
    while line:
        my_dice = line[0]
        last_move = line[2:].split(',')[-1].strip() if len(line) > 2 else ''
        print(decide(my_dice, last_move))
        line = sys.stdin.readline()