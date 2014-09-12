#!/usr/bin/env python3
import argparse
from collections import namedtuple
import json
from random import choice
import shlex
from statistics import mean
from subprocess import Popen, PIPE
import sys
import os
import signal
from time import sleep, time

TIMEOUT = 'timeout'

TIMEOUT = 10.130
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
        bots = {}
        for line in f:
            if line.startswith('#'):
                continue
            try:
                b = json.loads(line)
                bots[b['name']] = b
            except Exception as ex:
                print('[Exception] %s' % ex, file=sys.stderr)
    return bots

class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


def reverse_for_ilyin(line):
    """
    >>> reverse_for_ilyin('*')
    '*'
    >>> reverse_for_ilyin('1 11,12,13')
    '1 13,12,11'"""
    return line[0] + (' ' + ','.join(line[2:].split(',')[::-1]) if ' ' in line else '')


class Bot:
    def __init__(self, command_to_start, name, timeout_millis, version=2):
        self.command_to_start = command_to_start
        self.name = name
        self.version = version
        self.proc = Popen(shlex.split(self.command_to_start), universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.time_to_think_millis = timeout_millis
        self.time_left_millis = 0

    def communicate(self, *args, read_answer=True, **kwargs):
        assert len(args) == 1
        ros = args[0]

        if self.version == 1:  # version 1 bots can't parse game stats
            if ros.startswith('win') or ros.startswith('loss'):
                return

        start_time = time()
        print(ros, file=self.proc.stdin)
        if read_answer:
            answer = self.proc.stdout.readline().strip()
            return answer.strip(), int((time() - start_time) * 1000)

    def time_left(self, millis):
        self.time_left_millis += millis

    def get_millis_left(self):
        return self.time_to_think_millis - self.time_left_millis


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


def fight_once(bots, games_left):
    state = random_state()
    first_to_move = state.whos_turn
    winner = None
    status = 'ok'
    answer = ''
    while 1:
        if bots[state.whos_turn].get_millis_left() <= 0:
            winner = next_player(state.whos_turn)
            status = TIMEOUT
            answer = TIMEOUT
            break
        answer, time_spent = bots[state.whos_turn].communicate(state_to_string(state))
        bots[state.whos_turn].time_left(time_spent)
        if answer not in all_possible_actions(state.actions[-1] if state.actions else ''):
            winner = next_player(state.whos_turn)
            status = ILLEGAL_ACTION
            print('[ILLEGAL_MOVE] Got "%s" on state "%s"' % (answer, state_to_string(state)))
            break
        if answer == LIAR:
            winner = determine_winner(state)
            break
        state = RoundOneState(state.dices, next_player(state.whos_turn), state.actions + [answer])

    # send notifications that the game is over
    for i, b in enumerate(bots):
        w = 'win' if winner == i else 'loss'
        rival_dice = state.dices[next_player(i)]
        bots[i].communicate('%s %s %d %d' % (w, rival_dice, games_left, bots[i].get_millis_left()), read_answer=False)

    result = {'winner': winner,
              'status': status,
              'first_to_move': first_to_move,
              'round_len': len(state.actions) + 1,
              'actions': ','.join(state.actions + [answer])}
    return result


def percent(numerator, denominator):
    if denominator in {0, 0.0}:
        return 'NA'
    return '%.2f%%' % (numerator / denominator * 100)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    parser = argparse.ArgumentParser(description="The Liar's Dice game bots contest. 2nd round.")
    parser.add_argument('--games', type=int, help='how many games in a match (default=100)', default=100)
    parser.add_argument('--timeout', type=int, help='time given to play the whole match for every bot in millis',
                            default=1000)
    #parser.add_argument('--log', type=bool, help='', action='store_true', default=False)
    parser.add_argument('bot_names', help='bots fighting each other', nargs=2, default=['sample1', 'sample2'])
    args = parser.parse_args()
    print(args)

    bot_names = args.bot_names

    bot_instructions = read_bot_instructions()

    os.chdir('bots')

    bots = [Bot(bot['cmd'],
                     bot['name'],
                     args.timeout,
                     version=int(bot.get('version', 2)))
            for bot in [bot_instructions[b] for b in bot_names]]
    print(bot_names)

    with open('%s-vs-%s.log' % tuple(bot_names), 'w') as f:
        results = []
        games_count = args.games
        for i in range(games_count):
            if i % 1000 == 0:
                print(i)
            r = fight_once(bots, games_count - i)
            results.append(r)
            f.write('winner\t%s\tactions\t%s' % (r['winner'], r['actions']))
    print()

    games_count = len(results)
    for bot_id, bot in enumerate(bot_names):
        wins = len([r for r in results if r['winner'] == bot_id])
        print('{bot} won {bot_wins} of {total_games} -- {percent_of_wins}'.format(bot=bot,
                                                                                    bot_wins=wins,
                                                                                    total_games=games_count,
                                                                                    percent_of_wins=percent(wins, games_count)))
        when_first = len([r for r in results if r['first_to_move'] == bot_id == r['winner']])
        print('%s%% of wons having first move' % percent(when_first, wins))
        illegal_moves = len([r for r in results if (r['winner'] != bot_id) and (r['status'] == ILLEGAL_ACTION)])
        print('lost by illegal moves: %d (%s of all losses)' % (illegal_moves, percent(illegal_moves, games_count - wins)))
        timeouts = len([r for r in results if (r['winner'] != bot_id) and (r['status'] == TIMEOUT)])
        print('lost by timeouts: %d (%s of all losses)' % (timeouts, percent(timeouts, games_count - wins)))
        print()

    print('Mean round length is %0.2f turns' % mean([r['round_len'] for r in results]))






