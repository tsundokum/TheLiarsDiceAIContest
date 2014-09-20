#!/usr/bin/env python3
import sys

line = sys.stdin.readline()
while line:
    if len(line.strip()) == 1:
        print('15', flush=True)
    else:
        print('liar', flush=True)
    line = sys.stdin.readline()