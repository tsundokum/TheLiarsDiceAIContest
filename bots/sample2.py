#!/usr/bin/env python3
import sys

for line in sys.stdin:
    if len(line.strip()) == 1:
        print('1' + line.strip())
    else:
        print('liar')