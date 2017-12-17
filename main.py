#!/usr/bin/python3

# Documentation: See https://github.com/jjermann/dicedensity

from densities import *
from combatant import *


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
print("Expected winProbability of a spell caster with attackerDie+bonusAttacker against a defender with defenderDie (parametrized by attackerDie):")
print(get_plot(winProbability, plotWidth=60))
#print(get_simple_plot(winProbability))
print("\n")
print("Expected spellDuration (same situation as above):")
print(get_plot(expectedDuration))
print("\n")
print("All possible spell durations with their probabilities in case bonusAttacker = 10:")
print(durationDensity(10))

plot_image(winProbability)
plot_image(expectedDuration)
durationDensity(10).plotImage("durationDensity10")

# durationDensity(10) *given* the attacker wins:
#print(durationDensity(10).conditionalDensity(lambda k: k > 0))


# Two combatants fighting
# -----------------------

# 2.Neal Combatant
dnd2NealCombatant1 = Dnd2NealCombatant( \
    hp             = 20                ,\
    attackDie      = ad20              ,\
    bonusToHit     = 9                 ,\
    damageDie      = d8+d4             ,\
    bonusToDamage  = 3                 ,\
    ac             = 13                 \
)
dnd2NealCombatant2 = Dnd2NealCombatant( \
    hp             = 20                ,\
    attackDie      = d20               ,\
    bonusToHit     = 9                 ,\
    damageDie      = d8                ,\
    bonusToDamage  = 3                 ,\
    ac             = 18                 \
)

# New rules combatant (unfortunately the rules are not yet 100% clear)
combatant1 = Combatant(   \
  hp            = 20     ,\
  maxFatigue    = 10     ,\
  attackDie     = ad20   ,\
  bonusToHit    = 3      ,\
  damageDie     = d4     ,\
  bonusToDamage = 2      ,\
  evade         = 2      ,\
  armor         = 5      ,\
  resistance    = 0       \
)

combatant2 = Combatant(   \
  hp            = 20     ,\
  maxFatigue    = 10     ,\
  attackDie     = d20    ,\
  bonusToHit    = 1      ,\
  damageDie     = d8     ,\
  bonusToDamage = -1     ,\
  evade         = 5      ,\
  armor         = 10     ,\
  resistance    = 6       \
)

print("\n")
print("Expected damage of combatant1 against combatant2 for all attackRolls:")
print(combatant1.plotDamage(combatant2))
combatant1.plotDamageImage(combatant2)
print()

winProbability = combatant1.winProbability(combatant2, precise=False, maxError = 0.0001)
print("Chance of combatant1 to win against combatant2:             {:.2%}".format(winProbability))

winProbabilitySelf = combatant1.winProbability(combatant1, precise=False, maxError = 0.0001)
print("Chance of combatant1 to win against himself:                {:.2%}".format(winProbabilitySelf))

winProbabilitySelfRandom = combatant1.winProbability(combatant1, chanceDefenderStarts = 0.5, precise=False, maxError = 0.001)
print("Chance of combatant1 to win against himself (random start): {:.2%}".format(winProbabilitySelfRandom))
print()

print("Expected damage of dnd2NealCombatant1 against dnd2NealCombatant2 for all attackRolls:")
print(dnd2NealCombatant1.plotDamage(dnd2NealCombatant2))
print()
winProbability2Neal = dnd2NealCombatant1.winProbability(dnd2NealCombatant2, chanceDefenderStarts = 0.5, maxError = 0.005)
print("Chance of dnd2NealCombatant1 to win against dnd2NealCombatant2 (random start):          {:.2%}".format(winProbability2Neal))

hpDensityAfter3Rounds = dnd2NealCombatant1.hpDensity(dnd2NealCombatant2, 3)
print("HP distribution of dnd2NealCombatant1 after 3 rounds of combat against dnd2NealCombatant2:")
print(hpDensityAfter3Rounds)
print()
