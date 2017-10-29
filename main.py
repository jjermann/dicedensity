from densities import *


# Define some basic dice
# -----------------------------

ex   = DieExpr("d5+ad15+m2d7+dd2-2")
d2   = Die(2)
d3   = Die(3)
d4   = Die(4)
d6   = Die(6)
d8   = Die(8)
d10  = Die(10)
d12  = Die(12)
d20  = Die(20)
d100 = Die(100)
ad20 = AdvantageDie(20)
dd20 = DisadvantageDie(20)


# Some examples how to use this
# -----------------------------

# Probability that d6+d10 is lower or equal to d8
#print(d6+d10 <= d8)
#print("{:.4%}".format(d6+d10 <= d8))

# Probabilities for results of some example rolls
#print(d20+d20+4)
#print(d3*d6)
#print(ex)
#print(d20)
#print(ad20)
#print(dd20)

# Note that 3*d6 simulates a d6 die who's result is multiplied by 3, not d6+d6+d6
#print(3*d6)
# To get d6+d6+d6, one can use d6+d6+d6 or d6.arithMult(3) or DieExpr("m3d6")
#print(d6+d6+d6)
#print(d6.arithMult(3))
#print(DieExpr("m3d6"))


# Probabilities to find a certain number of rations of food when searching for "turnsToSearch" turns
# -----------------------------

twod6 = d6 + d6
turnsToSearch = 50
print(twod6.summedDensity(turnsToSearch))

#Expected number of rations after searching x turns:
#print(str.join("\n", list(map(lambda turns: "{:>12}\t{:>12.5f}".format(turns, twod6.summedDensity(turns).expected()), range(0,100+1)))))


