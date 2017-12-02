#!/usr/bin/python3

from densities import *


# Define some basic dice
# -----------------------------

ex   = DieExpr("d5+ad15+m2d7+dd2-2")
ex2  = ex.with_advantage()
ex3  = ex.with_disadvantage()
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
aad20 = d20.asMultiDensity(3).drop_lowest(2)
dd20 = DisadvantageDie(20)
ddd20 = d20.asMultiDensity(3).drop_highest(2)


# Some examples how to use this
# -----------------------------

# Probability that d6+d10 is lower or equal to d8
#print(d6+d10 <= d8)
#print("{:.4%}".format(d6+d10 <= d8))

# Probabilities for results of some example rolls
#print(d20+d20+4)
#print(d3*d6)
#print(ex)
#print(ex2)
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

#twod6 = d6 + d6
#turnsToSearch = 50
#print(twod6.summedDensity(turnsToSearch))

#Expected number of rations after searching x turns:s
#print(get_plot(lambda turns: twod6.summedDensity(turns).expected(), range(0,100 + 1), 70, 15))

#When using the lower result of rolling d6+d6 twice:
#print(twod6.with_disadvantage().summedDensity(turnsToSearch))


# MultiDensity examples
# -----------------------------

# The follwing describes rolling d2, d6 and d20 and then doing operations on the three rolls.
#mroll1 = MultiDensity(d2, d6, d20)
#print(mroll1.drop_highest(2))
#print(mroll1.drop_lowest())

# Take the largest of the three rolls
#print(mroll1.multiOp(lambda *a: max(a)))

# Note that MultiDensity(d2,d6).drop_lowest() is not the same as MultiDensity(d2,d6).with_advantage().
# with_advantage simply does the whole roll (of all dice) again and then takes the better final result
# wheris drop_lowest() will drop the lowest roll of a given list of rolls (here d2 and d6)
#mroll2 = MultiDensity(d2,d6)
# this ranges from 1 to 6
#print(mroll2.drop_lowest())
# this ranges from 2 to 8
#print(mroll2.with_advantage())


# Other operations with results
# -----------------------------

#def successCondition(bonusAttacker, bonusDefender):
#  def finalCondition(attackRoll, defendRoll):
#    if (defendRoll == 20):
#      return 0
#    if (defendRoll == 1):
#      return 1
#    if (attackRoll + bonusAttacker > defendRoll + bonusDefender):
#      return 1
#    else:
#      return 0
#  return finalCondition

# > 0 means the attacker wins, 0 means the defender wins
# in fact we specify the amount by which the attacker wins so it can be used for spellDuration as well
def spellDuration(bonusAttacker, bonusDefender):
  def finalDuration(attackRoll, defendRoll):
    if (defendRoll == 20):
      return 0
    if (defendRoll == 1):
      return max(1, (attackRoll + bonusAttacker) - (defendRoll + bonusDefender))
    if (attackRoll + bonusAttacker > defendRoll + bonusDefender):
      return (attackRoll + bonusAttacker) - (defendRoll + bonusDefender)
    else:
      return 0
  return finalDuration

# Win probability of attacker (cases where spellDuration > 0.0), parametrized by bonusAttacker
attackerDie = d20.asMultiDensity(2).drop_lowest(1)
defenderDie = d20
durationDensity = lambda bonusAttacker: MultiDensity(attackerDie, defenderDie).multiOp(spellDuration(bonusAttacker, 0))
winProbability = lambda bonusAttacker: durationDensity(bonusAttacker) > 0
#winProbability = lambda bonusAttacker: MultiDensity(attackerDie, defenderDie).multiOp(successCondition(bonusAttacker, 0)) > 0
expectedDuration = lambda bonusAttacker: durationDensity(bonusAttacker).expected()

#print(get_plot(winProbability, range(-20, 20 + 1), asPercentage = True))
print(get_plot(expectedDuration, range(-20, 20 + 1), plotWidth=50, maxP=30))
#print(get_simple_plot(winProbability, range(-20, 20 + 1)))
print("\n")
print(durationDensity(0))
# durationDensity(0) *given* the attacker wins
#print(durationDensity(0).conditionalDensity(lambda k: k > 0))

