#!/usr/bin/env python3
import sys

line = sys.stdin.readline()
while line:
    if len(line.strip()) == 1:
        print('15')
    else:
        print('liar')
    line = sys.stdin.readline()