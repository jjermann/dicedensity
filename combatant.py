
from densities import *

class Combatant:
  def __init__(self, hp, exhausts, attackDie, bonusToHit, damageDie, bonusToDamage, evade, armor, resistance):
    self.hp = hp
    self.exhausts = exhausts
    self.attackDie = attackDie
    self.bonusToHit = bonusToHit
    self.damageDie = damageDie
    self.bonusToDamage = bonusToDamage
    self.evade = evade
    self.armor = armor
    self.resistance = resistance

  def __str__(self):
    res = "HP = {}, Exhausts = {}".format(self.hp, self.exhausts)
    if self.isDead():
      res += " (DEAD)"
    if self.isUnconcious():
      res += " (Unconcious)"
    return res

  def __repr__(self):
    return self.__str__()

  def _state(self):
    #return (self.hp, self.exhausts, self.attackDie, self.bonusToHit, self.damageDie, self.bonusToDamage, self.evade, self.armor, self.resistance)
    return (self.hp, self.exhausts)

  def __hash__(self):
    return hash(self._state())

  def __eq__(self, other):
    if not isinstance(other, Combatant):
      raise NotImplemented
    return self._state() == other._state()

  def clone(self):
    return Combatant(self.hp, self.exhausts, self.attackDie, self.bonusToHit, self.damageDie, self.bonusToDamage, self.evade, self.armor, self.resistance)

  def damageDensity(self, other, attackRoll):
    if (attackRoll + self.bonusToHit) < other.evade:
      return Zero()

    if attackRoll + self.bonusToHit < other.evade + other.armor:
      armorHitDamage = self.damageDie.op(lambda a: max(0, a + self.bonusToDamage - other.resistance))
      return armorHitDamage

    criticalHits = math.floor(((attackRoll + self.bonusToHit) - (other.evade + other.armor)) / 5)
    criticalHitDamage = self.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + self.bonusToDamage))
    return criticalHitDamage

  def chanceToHit(self, other):
    isHit = lambda attackRoll: not isinstance(self.damageDensity(other, attackRoll), Zero)
    chance = sum([self.attackDie[k]*(1.0 if isHit(k) else 0.0) for k in self.attackDie.keys()])
    return chance

  def expectedDamage(self, other):
    return sum([self.attackDie[k]*self.damageDensity(other, k).expected() for k in self.attackDie.keys()])

  def plotDamage(self, other):
    res = ""
    res += "{:>12}\t{:>12.5f}".format("Expected", self.expectedDamage(other)) + "\n"
    res += "{:>12}\t{:>12.5%}".format("Hit chance", self.chanceToHit(other)) + "\n\n"
    res += "{:>12}\t{:>12}\t{}".format("Result", "Exp. damage", "Plot") + "\n"
    res += get_plot(lambda k: self.damageDensity(other, k).expected(), self.attackDie.keys())
    return res

  def plotDamageImage(self, other):
    def ExpectedDamage(attackRoll):
      return self.damageDensity(other, attackRoll).expected()
    inputs = self.attackDie.keys()
    xlabel = "Attack roll (Total expected damage: {})".format(self.expectedDamage(other))
    ylabel = "Expected damage"
    plot_image(ExpectedDamage, inputs = inputs, xlabel=xlabel, ylabel=ylabel)

  def isDead(self):
    return self.hp <= 0

  def isUnconcious(self):
    return (not self.isDead()) and self.exhausts <= 0

  def canFight(self):
    return not self.isDead() and not self.isUnconcious()

  def cantFight(self):
    return self.isDead() or self.isUnconcious()

  def _attackedCombatant(self, other, attackRoll):
    if (self.cantFight()):
      return other.clone()

    damageDensity = self.damageDensity(other, attackRoll)
    damage = damageDensity.expected()
    isHit = not isinstance(damageDensity, Zero)
    clone = other.clone()
    clone.hp -= damage
    if isHit:
      clone.exhausts -= 1
    return clone

  @staticmethod
  def _adjustedAttackDistribution(d, reversed=False):
    dNew = {}
    if reversed:
      for (attacker, defender) in d:
        for k in attacker.attackDie.keys():
          defenderNew = attacker._attackedCombatant(defender, k)
          if not (attacker, defenderNew) in dNew:
            dNew[(attacker, defenderNew)] = 0.0
          dNew[(attacker, defenderNew)] += attacker.attackDie[k]*d[(attacker, defender)]
    else:
      for (attacker, defender) in d:
        for k in defender.attackDie.keys():
          attackerNew = defender._attackedCombatant(attacker, k)
          if not (attackerNew, defender) in dNew:
            dNew[(attackerNew, defender)] = 0.0
          dNew[(attackerNew, defender)] += defender.attackDie[k]*d[(attacker, defender)]
    return dNew

  @staticmethod
  def _applyAttackRound(d):
    dNew1 = Combatant._adjustedAttackDistribution(d)
    dNew2 = Combatant._adjustedAttackDistribution(dNew1, reversed=True)
    return dNew2

  @staticmethod
  def combatDistribution(attacker, defender, rounds = 1):
    d = {(attacker, defender): 1.0}
    for round in range(rounds):
      d = Combatant._applyAttackRound(d)
    return d

  @staticmethod
  def eventProbability(d, cond):
    return sum([d[(attacker, defender)] for (attacker, defender) in d if cond(attacker, defender)])

  @staticmethod
  def combatEventProbability(attacker, defender, cond, rounds = 1):
    d = Combatant.combatDistribution(attacker, defender, rounds)
    p = Combatant.eventProbability(d, cond)
    return p

  @staticmethod
  def resultDensity(d, op):
    density = {}
    keys = set([op(attacker, defender) for (attacker, defender) in d])
    for k in keys:
      density[k] = Combatant.eventProbability(d, lambda attacker, defender: k == op(attacker, defender))
    return Density(density)

  @staticmethod
  def combatResultDensity(attacker, defender, op, rounds = 1):
    d = Combatant.combatDistribution(attacker, defender, rounds)
    return Combatant.resultDensity(d, op)

  def hpDensity(self, defender, rounds = 1):
    op = lambda attacker, defender: attacker.hp
    return Combatant.combatResultDensity(self, defender, op, rounds)

  def winProbability(self, defender, maxError = 0.001):
    d = {(self, defender): 1.0}

    undecidedCond = lambda attacker, defender: attacker.canFight() and defender.canFight()
    while Combatant.eventProbability(d, undecidedCond) > maxError:
      d = Combatant._applyAttackRound(d)

    winCond = lambda attacker, defender: defender.cantFight()
    return Combatant.eventProbability(d, winCond)
