from random import random
import re


def myturn(q):

    my, turns = q.strip().split() if len(q) != 1 else [q, ""]

    if turns == "":
        # my turn is the first
        if my in ["*", "5"]:
            return "15"
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
                return("2" + p)
            else:
                if int(p) < int(my):
                    return("1" + my)
                elif int(p) == int(my):
                    return("2" + my)
                else:
                    r = random()
                    if r < 0.5:
                        return("1*")
                    else:
                        return("liar")

    else:
        if re.match("1[1-5],1\*", turns):
            return("2" + my)
        else:
            return("liar") # or I lost

assert myturn("*") == "15"
assert myturn("5 15") == "25"
assert myturn("* 1*,2*") == "liar"


import sys

for l in sys.stdin:
    print(myturn(l.strip()))