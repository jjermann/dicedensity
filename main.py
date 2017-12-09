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
#print(get_plot(lambda turns: twod6.summedDensity(turns).expected(), range(0,100 + 1), plotWidth=70, maxP=15))

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

def durationDensity(bonusAttacker):
  return MultiDensity(attackerDie, defenderDie).multiOp(spellDuration(bonusAttacker, 0))

def winProbability(bonusAttacker):
  return durationDensity(bonusAttacker) > 0

#winProbability = lambda bonusAttacker: MultiDensity(attackerDie, defenderDie).multiOp(successCondition(bonusAttacker, 0)) > 0

def expectedDuration(bonusAttacker):
  return durationDensity(bonusAttacker).expected()

# Plotting
# -----------------------------
# get_plot(p, inputs = range(-20, 20 + 1), plotWidth = 50, minP = None, maxP = None, asPercentage = False, centered = True)
# - p is the function to plot, e.g. "lambda k: durationDensity(k).expected()" or "winProbability"
# - inputs are the function inputs, e.g. range(-20, 20 + 1)
# - plotWidth is the plot size (default 50)
# - minP/maxP are the desired range for plotting,
#   by default minP is 0 or the minimal result if that's below zero
#   by default maxP is the maximal result
# - asPercentage determines if the results are shown as percentages (default False)
# - centered determines if negative results are drawn "away from zero" or not (default True)
# In case only the second column is desired (e.g. to copy results), replace "get_plot" by "get_simple_plot"
#
# Example:
# print(get_plot(winProbability, range(-20, 20 + 1), plotWidth = 50, minP = 0.0, maxP = 1.0, centered = True, asPercentage = True))
#
# For graphical plotting use plot_image(function, inputs, name, xlabel, ylabel, fmt, **kwargs),
# Defaults are: inputs=range(-20, 20 + 1), name=<name of function or "plot">, xlabel="Input", ylabel="Output", fmt='-'
# Densities can also be plotted as follows: d.plotImage(name, xlabel, ylabel, fmt, **kwargs),
# Defaults are: name="plot", xlabel="Result", ylabel="Probability", fmt='-' (solid line)
# Graphical plots are saved as separate image (with given name)
# In both cases additional plotting options can be given. For possible plotting formats and other options see:
# https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html#matplotlib.pyplot.plot
#
# Examples:
# plot_image(expectedDuration, name="expectedDuration", )
# durationDensity(10).plotImage(fmt='--')
# (d20+d20+d20).plotImage("3d20")
#
# For more complex plotting, pyplot should be used directly, example:
#fig = plt.figure()
#plt.title("Duration density given attacker wins")
#plt.xlabel("Duration")
#plt.ylabel("Probability")
#for bonusAttacker in range(-10,10+1):
#  d = durationDensity(bonusAttacker).conditionalDensity(lambda k: k>0)
#  plt.plot(d.keys(), d.values(), '-')
#plt.savefig("durationDensityAttackerWins")
#plt.close(fig)
#
# Here is another example that plots d20+d20+d20 and it's normal approximation
#fig = plt.figure()
#plt.title("3d20 and normal approximation")
#plt.xlabel("Roll / Input")
#plt.ylabel("Probability")
#m3d20 = d20 + d20 + d20
#plt.plot(m3d20.keys(), m3d20.values(), '-r')
#normalApproximation = m3d20.normalApproximation
#plt.plot(m3d20.keys(), [normalApproximation(k) for k in m3d20.keys()], '-b')
#plt.savefig("3d20vsNormal")
#plt.close(fig)

print(get_plot(winProbability, plotWidth=60))
#print(get_simple_plot(winProbability))
print("\n")
print(get_plot(expectedDuration))
print("\n")
print(durationDensity(10))

plot_image(winProbability)
plot_image(expectedDuration)
durationDensity(10).plotImage("durationDensity10")

# durationDensity(10) *given* the attacker wins:
#print(durationDensity(10).conditionalDensity(lambda k: k > 0))

