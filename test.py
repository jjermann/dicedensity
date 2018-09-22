#!/usr/bin/python3

# Documentation: See https://github.com/jjermann/dicedensity

from densities import *
from combatant import *

def nealDamageDensity(attacker, defender, attackRoll):
  excess = attackRoll + attacker.bonusToHit - defender.evade
  if (excess < 0):
    return Zero()

  if attacker.criticalThreshold is None:
    criticalHits = 0
  else:
    criticalHits = excess // attacker.criticalThreshold
  damage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage))
  return damage

ogreBro = DndNealTestCombatant(   \
  hp                  = 100      ,\
  bonusToHit          = 0        ,\
  bonusToHitUnarmored = 0        ,\
  damageDie           = d10+d10  ,\
  bonusToDamage       = 0        ,\
  evade               = 20       ,\
  criticalThreshold   = 30       ,\
  armor               = 0        ,\
  maxFatigue          = None
)

warrior = DndNealTestCombatant( \
  hp                  = 50       ,\
  bonusToHit          = 31       ,\
  bonusToHitUnarmored = 0        ,\
  damageDie           = d6+d6    ,\
  bonusToDamage       = 0        ,\
  evade               = 49       ,\
  criticalThreshold   = 32       ,\
  armor               = 0        ,\
  maxFatigue          = None
)

print("Chance of OgreBro to hit Warrior:           {:>12.2%}".format(ogreBro.chanceToHit(warrior)))
print("Expected damage of OgreBro against Warrior: {:>12.6}".format(ogreBro.expectedDamage(warrior)))
print()
print("Chance of Warrior to hit OgreBro:           {:>12.2%}".format(warrior.chanceToHit(ogreBro)))
print("Expected damage of Warrior against OgreBro: {:>12.6}".format(warrior.expectedDamage(ogreBro)))

#print(ogreBro.winProbability(warrior, chanceDefenderStarts = 0.5))

