#!/usr/bin/env python3
from collections import namedtuple
from random import choice
import shlex
from statistics import mean
from subprocess import Popen, PIPE
import sys
import os
import signal

TIMEOUT = 'timeout'

TIMEOUT = 0.130
ILLEGAL_ACTION = 'illegal_action'
DELIM = ' -> '
LIAR = 'liar'

nominals = list([str(i) for i in range(1, 6)])
dice_values = nominals + ['*']

RoundOneState = namedtuple('RoundOneState', 'dices whos_turn actions')


def create_triple(index):
    """
    >>> create_triple(0)
    ['11', '12', '13', '14', '15', '1*', '21', '22', '23', '24', '25']
    >>> create_triple(5)
    ['111', '112', '113', '114', '115', '6*', '121', '122', '123', '124', '125']"""
    return [str(index * 2 + 1) + n for n in nominals] + \
           [str(index + 1) + '*'] + \
           [str(index * 2 + 2) + n for n in nominals]

bets = create_triple(0) + ['2*'] + ['liar']



def next_player(player_id):
    """
    >>> next_player(0)
    1
    >>> next_player(1)
    0"""
    return (player_id + 1) % 2


def determine_winner(ros: RoundOneState):
    """Return index of a winner
    >>> determine_winner(RoundOneState(['1', '1'], 0, ['12']))
    0
    >>> determine_winner(RoundOneState(['1', '*'], 1, ['11']))
    0
    >>> determine_winner(RoundOneState(['4', '*'], 0, ['24']))
    1
    >>> determine_winner(RoundOneState(['*', '4'], 1, ['25']))
    1
    >>> determine_winner(RoundOneState(['*', '4'], 0, ['2*']))
    0"""
    if len([d for d in ros.dices if d in ['*', ros.actions[-1][1]]]) >= int(ros.actions[-1][:-1]):
        return next_player(ros.whos_turn)
    else:
        return ros.whos_turn


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


def random_dice():
    return choice(dice_values)


def read_bot_instructions():
    with open('bots.list') as f:
        bots = []
        for line in f:
            if line.startswith('#') or (DELIM not in line):
                continue
            bots.append(line.strip().split(DELIM, maxsplit=1))
    return dict(bots)


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


def create_bot(command_to_start):
    proc = Popen(shlex.split(command_to_start), universal_newlines=True, stdin=PIPE, stdout=PIPE)
    def f(ros):
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.setitimer(signal.ITIMER_REAL, TIMEOUT)

        print(ros, file=proc.stdin)
        answer = proc.stdout.readline().strip()
        signal.alarm(0)
        return answer
    return f


def random_state():
    return RoundOneState([random_dice(), random_dice()], choice([0, 1]), [])


def state_to_string(s: RoundOneState):
    """
    >>> state_to_string(RoundOneState(['1', '2'], 0, []))
    '1'
    >>> state_to_string(RoundOneState(['1', '2'], 1, ['11', '12']))
    '2 11,12'"""
    actions = ' ' + ','.join(s.actions) if s.actions else ''
    return s.dices[s.whos_turn] + actions


def fight_once(bots):
    state = random_state()
    first_to_move = state.whos_turn
    winner = None
    status = 'ok'
    while 1:
        try:
            answer = bots[state.whos_turn](state_to_string(state))
        except Alarm:
            status = TIMEOUT
            winner = next_player(state.whos_turn)
            break
        if answer not in all_possible_actions(state.actions[-1] if state.actions else ''):
            winner = next_player(state.whos_turn)
            status = ILLEGAL_ACTION
            break
        if answer == LIAR:
            winner = determine_winner(state)
            break
        state = RoundOneState(state.dices, next_player(state.whos_turn), state.actions + [answer])
    return {'winner': winner,
            'status': status,
            'first_to_move': first_to_move,
            'round_len': len(state.actions) + 1}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    if len(sys.argv) != 3:
        print('Usage: python main.py bot1 bot2', file=sys.stderr)
        sys.exit(1)

    bot_names = sys.argv[1:3]

    bot_instructions = read_bot_instructions()
    print(bot_instructions)

    os.chdir('bots')

    bots = [create_bot(bot_instructions[bot_name]) for bot_name in bot_names]

    results = [fight_once(bots) for _ in range(100)]
    games_count = len(results)
    for bot_id, bot in enumerate(bot_names):
        wins = len([r for r in results if r['winner'] == bot_id])
        print('{bot} won {bot_wins} of {total_games} -- {percent_of_wins:.1f}%'.format(bot=bot,
                                                                                  bot_wins=wins,
                                                                                  total_games=games_count,
                                                                                  percent_of_wins=wins / games_count * 100))
        when_first = len([r for r in results if r['first_to_move'] == bot_id == r['winner']])
        print('%.1f%% of wons having first move' % (when_first / wins * 100))
        illegal_moves = len([r for r in results if (r['winner'] != bot_id) and (r['status'] == ILLEGAL_ACTION)])
        print('lost by illegal moves: %d (%.2f%% of all losses)' % (illegal_moves, illegal_moves / (games_count - wins) * 100))
        timeouts = len([r for r in results if (r['winner'] != bot_id) and (r['status'] == TIMEOUT)])
        print('lost by timeouts: %d (%.2f%% of all losses)' % (timeouts, timeouts / (games_count - wins) * 100))
        print()

    print('Mean round length is %0.2f turns' % mean([r['round_len'] for r in results]))






