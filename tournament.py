#!/usr/bin/env python3
import argparse
import itertools
from multiprocessing import Pool
from subprocess import Popen, PIPE
from random import shuffle

import smtplib
from email.mime.text import MIMEText

LOG = 'tournament.log'

games = 1000
timeout = 1000 + 5000

def match(pair):
    print('>>>>>>> %s vs %s' % tuple(pair))
    p = Popen(['python3', 'main.py', '--games', str(games),
                                     '--timeout', str(timeout)] + pair, universal_newlines=True, stdout=PIPE)
    (result, _) = p.communicate()
    with open(LOG, 'a') as f:
        print(str(result), file=f)
        print('=' * 60, file=f)



if __name__ == '__main__':
    import doctest
    doctest.testmod()

    parser = argparse.ArgumentParser(description="The Liar's Dice game bots contest. 2nd round.")
    parser.add_argument('--games', type=int, help='how many games in a match (default=100)', default=games)
    parser.add_argument('--timeout', type=int, help='time given to play the whole match for every bot in millis',
                            default=timeout)
    parser.add_argument('bot_names', help='bots fighting each other', nargs='+', default=['sample1', 'sample2'])

    args = parser.parse_args()
    bots = args.bot_names

    games = args.games
    timeout = args.timeout

    with open(LOG, 'w') as f:
        pass

    pairs = [[b1, b2] for b1, b2 in itertools.product(bots, bots) if b1 < b2]
    shuffle(pairs)
    pool = Pool()

    pool.map(match, pairs)


