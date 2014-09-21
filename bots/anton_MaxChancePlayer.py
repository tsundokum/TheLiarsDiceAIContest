#!/usr/bin/env python3

import sys

LIAR = "liar"


def decide(input):
    if ' ' in input:
        myValue, previousMoves = input.split(' ', 1)
        previousMoves = previousMoves.split(',')
    else:
        myValue = input.split(' ', 1)[0]
        previousMoves = []

    if not previousMoves:
        return "11"
    else:
        prevCount = int(previousMoves[-1][:-1])
        prevValue = previousMoves[-1][-1]

        if prevCount >= 2:
            if (myValue == "*") and (len(previousMoves) >= 2):
                prevPrevCount = int(previousMoves[-2][:-1])
                prevPrevValue = previousMoves[-2][-1]
                if (prevValue == prevPrevValue) and (prevCount == 2) and (prevPrevCount == 1):
                    return "2*"  # try 2 stars, we have a chance to win

            return LIAR  # it's better to check
    # prevCount is 1

    if myValue == "*":
        # i have '*'
        return "2%s" % prevValue  # double opponent's move
    else:
        if prevValue == "*":
            return LIAR  # don't believe
        else:
            if prevValue < myValue:
                return "1%s" % myValue  # switch to my dice
            elif prevValue == myValue:
                return "2%s" % myValue  # two dice like mine
            else:
                # prevValue > myValue
                return LIAR  # do not believe, no other chances to win


if __name__ == '__main__':
    line = sys.stdin.readline()
    while line:
        print(decide(line.strip()), flush=True)
        line = sys.stdin.readline()