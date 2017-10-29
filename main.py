#!/usr/bin/python3

from densities import *


# Define some basic dice
# -----------------------------

ex   = DieExpression("d5+ad15+m2d7+dd2-2")
d2   = DieDensity(2)
d3   = DieDensity(3)
d4   = DieDensity(4)
d6   = DieDensity(6)
d8   = DieDensity(8)
d10  = DieDensity(10)
d12  = DieDensity(12)
d20  = DieDensity(20)
d100 = DieDensity(100)
ad20 = AdvantageDieDensity(20)
dd20 = DisadvantageDieDensity(20)


# Some examples how to use this
# -----------------------------

# Probability that d6+d10 is lower or equal to d8
#print(d6+d10 <= d8)
#print("{:.4%}".format(d6+d10 <= d8))

# Probabilities for results of some example rolls
#print(d20+d20+4)
#print(d3*d6)
#print(ex)
#print(ad20)
#print(dd20)


# Probabilities to find a certain number of rations of food when searching for "turnsToSearch" turns
# -----------------------------

twod6 = d6 + d6
#This could also be used for twod6:
twod6 = d6.arithMult(2)
turnsToSearch = 50
print(twod6.summedDensity(turnsToSearch))

