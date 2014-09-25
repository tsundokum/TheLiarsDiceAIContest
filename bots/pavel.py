from random import random
import re


def myturn(q):

    my, turns = q.strip().split() if len(q) != 1 else [q, ""]

    if turns == "":
        # my turn is the first
        if my in ["*", "5"]:
            return("1" + my)
        else:
            r = random()
            return "1" + my if r < 0.5 else "15" # bluff

    elif len(turns) == 2:
        # i am the second
        n, p = turns[0], turns[1]
        if int(n) >= 2:
            return("liar")
        if p == "*": 
            return("2" + my)
        else:
            if my == "*":
                return("1*")
            else:
                if int(p) < int(my):
                    return("1" + my)
                elif int(p) == int(my):
                    return("2" + my)    
                else:
                    return("liar")

    elif len(turns) == 4:
        if re.match("1[1-5],1\*", turns):
            return("2" + my)
        else:
            return("liar") # or I lost

    else:
        return("liar")

assert myturn("*") == "1*"
assert myturn("5 15") == "25"
assert myturn("* 1*,2*") == "liar"


import sys

l = sys.stdin.readline()
while l:
    print(myturn(l.strip()))
    sys.stdout.flush()
    l = sys.stdin.readline()