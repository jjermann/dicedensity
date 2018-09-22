#!/usr/bin/python3

# Documentation: See https://github.com/jjermann/dicedensity

from densities import *
from combatant import *

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
  bonusToHitUnarmored = 31       ,\
  damageDie           = d6+d6    ,\
  bonusToDamage       = 0        ,\
  evade               = 49       ,\
  criticalThreshold   = 32       ,\
  armor               = 0        ,\
  maxFatigue          = None
)

ogreHitWarrior = ogreBro.chanceToHit(warrior)
ogreDmgAgainstWarrior = ogreBro.expectedDamage(warrior)
warriorHitOgre = warrior.chanceToHit(ogreBro)
warriorDmgAgainstOgre = warrior.expectedDamage(ogreBro)

print("Chance of OgreBro to hit Warrior:           {:>12.2%}".format(ogreHitWarrior))
print("Expected damage of OgreBro against Warrior: {:>12.6}".format(ogreDmgAgainstWarrior))
print()
print("Chance of Warrior to hit OgreBro:           {:>12.2%}".format(warriorHitOgre))
print("Expected damage of Warrior against OgreBro: {:>12.6}".format(warriorDmgAgainstOgre))
print()

p = ogreBro.simpleWinProbability(warrior)
print("Win probability of OgreBro against Warrior: {:>12.2%}".format(p))
