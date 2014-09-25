#!/usr/bin/env python3

from random import random
import sys

LIAR = "liar"

def switch_11(myValue):
	r = random()
	return {
	"1": "21",
	"2": "liar" if r<0.5 else "15",
	"3": "liar" if r<0.5 else "15",
	"4": "liar" if r<0.5 else "15" if r<0.85 else "14",
	"5": "15",
	"*": "15"
}.get(myValue)

def switch_12(myValue):
	r = random()
	return {
	"1": "liar",
	"2": "22",
	"3": "liar" if r<0.3 else "15",
	"4": "liar" if r<0.3 else "15",
	"5": "15",
	"*": "15"
}.get(myValue)

def switch_13(myValue):
	r = random()
	return {
	"1": "liar" if r<0.58 else "15",
	"2": "liar" if r<0.58 else "15",
	"3": "23",
	"4": "liar" if r<0.58 else "15",
	"5": "15",
	"*": "15"
}.get(myValue)

def switch_14(myValue):
	r = random()
	return {
	"1": "liar" if r<0.58 else "15",
	"2": "liar" if r<0.58 else "15",
	"3": "liar" if r<0.58 else "15",
	"4": "24",
	"5": "15",
	"*": "15"
}.get(myValue)

def switch_15(myValue):
	r = random()
	return {
	"1": "liar" if r<0.6 else "21",
	"2": "liar" if r<0.6 else "22",
	"3": "liar" if r<0.6 else "23",
	"4": "liar" if r<0.6 else "24",
	"5": "25",
	"*": "25"
}.get(myValue)

def switch_1x(prevValue, myValue):
	r = random()
	return {
	"1": switch_11(myValue),
	"2": switch_12(myValue),
	"3": switch_13(myValue),
	"4": switch_14(myValue),
	"5": switch_15(myValue),
	"*": "25" if myValue == "*" else "liar" if r<0.3333 else "2" + myValue
}.get(prevValue, myValue)

def decide(input):
	if ' ' in input:
		myValue, previousMoves = input.split(' ', 1)
		previousMoves = previousMoves.split(',')
	else:
		myValue = input.split(' ', 1)[0]
		previousMoves = []

	if not previousMoves:
		if myValue == "*" or myValue == "5":
			return "15"
		elif myValue == "4":
			return "14"
		else:
			r = random()
			if r < 0.55555555:
				return "14"		
			else:
				return "15"
	else:
		prevCount = int(previousMoves[-1][:-1])
		prevValue = previousMoves[-1][-1]

		if prevCount >= 2:
			return LIAR
#		if len(previousMoves) >= 2 and prevValue == "5":
#			return "liar"

    # prevCount is 1
	return switch_1x(prevValue, myValue)


if __name__ == '__main__':
    line = sys.stdin.readline()
    while line:
        print(decide(line.strip()), flush=True)
        line = sys.stdin.readline()
