#!/usr/bin/env python3
import sys

for line in sys.stdin:
    if len(line.strip()) == 1:
        print('15')
    else:
        print('liar')