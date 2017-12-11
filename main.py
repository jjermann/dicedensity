#!/usr/bin/python3

# Documentation: See https://github.com/jjermann/dicedensity

from densities import *
from combatant import *

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


# Probabilities to find a certain number of rations of food when searching for "turnsToSearch" turns
# --------------------------------------------------------------------------------------------------

#twod6 = d6 + d6
#turnsToSearch = 50
#print(twod6.summedDensity(turnsToSearch))

#Expected number of rations after searching x turns:s
#print(get_plot(lambda turns: twod6.summedDensity(turns).expected(), range(0,100 + 1), plotWidth=70, maxP=15))

#When using the lower result of rolling d6+d6 twice:
#print(twod6.with_disadvantage().summedDensity(turnsToSearch))


# Comparing two rolls and determine e.g. spell durations from it
# --------------------------------------------------------------

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

def expectedDuration(bonusAttacker):
  return durationDensity(bonusAttacker).expected()

# Plotting
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


# Two combatants fighting
# -----------------------

combatant1 = Combatant(   \
  hp            = 20     ,\
  exhausts      = 10     ,\
  attackDie     = ad20   ,\
  bonusToHit    = 3      ,\
  damageDie     = d8+d4  ,\
  bonusToDamage = 2      ,\
  evade         = 2      ,\
  armor         = 5      ,\
  resistance    = 0       \
)

combatant2 = Combatant(   \
  hp            = 20     ,\
  exhausts      = 10     ,\
  attackDie     = d20    ,\
  bonusToHit    = 1      ,\
  damageDie     = d8     ,\
  bonusToDamage = -1     ,\
  evade         = 4      ,\
  armor         = 10     ,\
  resistance    = 6       \
)

print("\n")
print(combatant1.plotDamage(combatant2))
combatant1.plotDamageImage(combatant2)
