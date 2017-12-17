
from densities import *

class Combatant:
  def __init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, evade, armor = 0, resistance = 0, maxFatigue = None, fatigue = 0, damageDensity = None):
    self.hp = hp
    self.maxFatigue = maxFatigue
    self.fatigue = fatigue
    self.attackDie = attackDie
    self.bonusToHit = bonusToHit
    self.damageDie = damageDie
    self.bonusToDamage = bonusToDamage
    self.evade = evade
    self.armor = armor
    self.resistance = resistance
    if damageDensity is None:
      self._damageDensity = Combatant.defaultDamageDensity
    else:
      self._damageDensity = damageDensity

  def __str__(self):
    res = "HP = {}".format(self.hp)
    if not self.maxFatigue is None:
      res += ", Fatigue = {}/{}".format(self.fatigue, self.maxFatigue)
    if self.isDead():
      res += " (DEAD)"
    else:
      res += " (Fatigue: {})".format(self.fatigueState())
    return res

  def __repr__(self):
    return self.__str__()

  def _state(self):
    #return (self.hp, self.fatigue, self.attackDie, self.bonusToHit, self.damageDie, self.bonusToDamage, self.evade, self.armor, self.resistance, self.maxFatigue)
    return (self.hp, self.fatigue)

  def __hash__(self):
    return hash(self._state())

  def __eq__(self, other):
    if not isinstance(other, Combatant):
      raise NotImplemented
    return self._state() == other._state()

  def clone(self):
    return Combatant(self.hp, self.attackDie, self.bonusToHit, self.damageDie, self.bonusToDamage, self.evade, self.armor, self.resistance, self.maxFatigue, self.fatigue, self._damageDensity)

  @staticmethod
  def defaultDamageDensity(attacker, defender, attackRoll):
    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade:
      return Zero()

    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade + defender.armor:
      armorHitDamage = attacker.damageDie.op(lambda a: max(0, a + attacker.bonusToDamage - defender.resistance))
      return armorHitDamage

    criticalHits = math.floor(((attackRoll + attacker.bonusToHit + attacker.fatigueModifier()) - (defender.evade + defender.armor)) / 5)
    damage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage))
    return damage

  @staticmethod
  def dndDamageDensity(attacker, defender, attackRoll):
    minValue = min(attacker.attackDie.values())
    maxValue = max(attacker.attackDie.values())
    if attackRoll == minValue:
      return Zero()
    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade and attackRoll < maxValue:
      return Zero()

    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade + defender.armor:
      armorHitDamage = attacker.damageDie.op(lambda a: max(0, a + attacker.bonusToDamage - defender.resistance))
      return armorHitDamage

    criticalHits = math.floor(((attackRoll + attacker.bonusToHit + attacker.fatigueModifier()) - (defender.evade + defender.armor)) / 5)
    criticalHitDamage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage))
    return criticalHitDamage

  def fatigueState(self):
    if self.maxFatigue is None:
      return "None"
    if self.fatigue < self.maxFatigue / 4.0:
      return "None"
    elif self.fatigue < 2*self.maxFatigue / 4.0:
      return "Light"
    elif self.fatigue < 3*self.maxFatigue / 4.0:
      return "Medium"
    elif self.fatigue < self.maxFatigue:
      return "Heavy"
    else:
      return "Unconscious"

  def fatigueModifier(self):
    fatigueState = self.fatigueState()
    if fatigueState == "None":
      return 0
    if fatigueState == "Light":
      return -1
    if fatigueState == "Medium":
      return -3
    if fatigueState == "Heavy":
      return -5
    if fatigueState == "Unconscious":
      return -5

  def damageDensity(self, defender, attackRoll):
    return self._damageDensity(self, defender, attackRoll)

  def chanceToHit(self, defender):
    isHit = lambda attackRoll: not isinstance(self.damageDensity(defender, attackRoll), Zero)
    chance = sum([self.attackDie[k]*(1.0 if isHit(k) else 0.0) for k in self.attackDie.keys()])
    return chance

  def expectedDamage(self, defender):
    return sum([self.attackDie[k]*self.damageDensity(defender, k).expected() for k in self.attackDie.keys()])

  def plotDamage(self, defender):
    res = ""
    res += "{:>12}\t{:>12.5f}".format("Expected", self.expectedDamage(defender)) + "\n"
    res += "{:>12}\t{:>12.5%}".format("Hit chance", self.chanceToHit(defender)) + "\n\n"
    res += "{:>12}\t{:>12}\t{}".format("Result", "Exp. damage", "Plot") + "\n"
    res += get_plot(lambda k: self.damageDensity(defender, k).expected(), self.attackDie.keys())
    return res

  def plotDamageImage(self, defender):
    def ExpectedDamage(attackRoll):
      return self.damageDensity(defender, attackRoll).expected()
    inputs = self.attackDie.keys()
    xlabel = "Attack roll (Total expected damage: {})".format(self.expectedDamage(defender))
    ylabel = "Expected damage"
    plot_image(ExpectedDamage, inputs = inputs, xlabel=xlabel, ylabel=ylabel)

  def isDead(self):
    return self.hp <= 0

  def isUnconscious(self):
    return (not self.isDead()) and (not self.maxFatigue is None) and self.fatigue >= self.maxFatigue

  def canFight(self):
    return not self.isDead() and not self.isUnconscious()

  def cantFight(self):
    return self.isDead() or self.isUnconscious()

  def _attackedCombatantDistribution(self, defender, attackRoll):
    d = {}
    if (self.cantFight()):
      return {defender.clone(): 1.0}

    damageDensity = self.damageDensity(defender, attackRoll)
    isHit = not isinstance(damageDensity, Zero)
    applyFatigue = isHit and not defender.maxFatigue is None and defender.fatigue < defender.maxFatigue

    if not isHit:
      return {defender.clone(): 1.0}

    d = {}
    for damage in damageDensity.keys():
      clone = defender.clone()
      clone.hp -= damage
      clone.hp = max(0, clone.hp)
      if applyFatigue:
        clone.fatigue += 1
      if not clone in d:
        d[clone] = 0.0
      d[clone] += damageDensity[damage]
    return d

  def _expectedAttackedCombatant(self, defender, attackRoll):
    if (self.cantFight()):
      return defender.clone()

    damageDensity = self.damageDensity(defender, attackRoll)
    damage = damageDensity.expected()
    isHit = not isinstance(damageDensity, Zero)
    clone = defender.clone()
    clone.hp -= damage
    clone.hp = max(0, clone.hp)
    if isHit and not clone.maxFatigue is None and clone.fatigue < clone.maxFatigue:
      clone.fatigue += 1
    return clone

  @staticmethod
  def _adjustedAttackDistribution(d, reversed=False, precise=True):
    dNew = {}
    if reversed:
      for (attacker, defender) in d:
        for k in defender.attackDie.keys():
          if precise:
            attackerD = defender._attackedCombatantDistribution(attacker, k)
            for attackerNew in attackerD:
              if not (attackerNew, defender) in dNew:
                dNew[(attackerNew, defender)] = 0.0
              dNew[(attackerNew, defender)] += defender.attackDie[k]*d[(attacker, defender)]*attackerD[attackerNew]
          else:
            attackerNew = defender._expectedAttackedCombatant(attacker, k)
            if not (attackerNew, defender) in dNew:
              dNew[(attackerNew, defender)] = 0.0
            dNew[(attackerNew, defender)] += defender.attackDie[k]*d[(attacker, defender)]
    else:
      for (attacker, defender) in d:
        for k in attacker.attackDie.keys():
          if precise:
            defenderD = attacker._attackedCombatantDistribution(defender, k)
            for defenderNew in defenderD:
              if not (attacker, defenderNew) in dNew:
                dNew[(attacker, defenderNew)] = 0.0
              dNew[(attacker, defenderNew)] += attacker.attackDie[k]*d[(attacker, defender)]*defenderD[defenderNew]
          else:
            defenderNew = attacker._expectedAttackedCombatant(defender, k)
            if not (attacker, defenderNew) in dNew:
              dNew[(attacker, defenderNew)] = 0.0
            dNew[(attacker, defenderNew)] += attacker.attackDie[k]*d[(attacker, defender)]
    return dNew

  @staticmethod
  def _applyAttackRound(d, precise=True):
    dNew1 = Combatant._adjustedAttackDistribution(d, precise=precise)
    dNew2 = Combatant._adjustedAttackDistribution(dNew1, reversed=True, precise=precise)
    return dNew2

  @staticmethod
  def combatDistribution(attacker, defender, rounds = 1, chanceDefenderStarts = None, precise=True):
    d = {(attacker, defender): 1.0}
    if not chanceDefenderStarts is None:
      d = Combatant.randomizeInitialAttacker(d, chanceDefenderStarts, precise=precise)

    for round in range(rounds):
      d = Combatant._applyAttackRound(d, precise=precise)
    return d

  @staticmethod
  def eventProbability(d, cond):
    return sum([d[(attacker, defender)] for (attacker, defender) in d if cond(attacker, defender)])

  @staticmethod
  def combatEventProbability(attacker, defender, cond, rounds = 1, chanceDefenderStarts = None, precise=True):
    d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise=precise)
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
  def combatResultDensity(attacker, defender, op, rounds = 1, chanceDefenderStarts = None, precise=True):
    d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise=precise)
    return Combatant.resultDensity(d, op)

  def hpDensity(self, defender, rounds = 1, chanceDefenderStarts = None, precise=True):
    op = lambda attacker, defender: attacker.hp
    return Combatant.combatResultDensity(self, defender, op, rounds, chanceDefenderStarts, precise=precise)

  @staticmethod
  def randomizeInitialAttacker(d, chanceDefenderStarts = 0.5, precise=True):
      dAttackerFirst = d
      dDefenderFirst = Combatant._adjustedAttackDistribution(d, reversed=True, precise=precise)
      dNew = {}
      for (attacker, defender) in dAttackerFirst:
        p = dAttackerFirst[(attacker, defender)] * (1.0 - chanceDefenderStarts)
        if not (attacker, defender) in dNew:
          dNew[(attacker, defender)] = p
        else:
          dNew[(attacker, defender)] += p
      for (attacker, defender) in dDefenderFirst:
        p = dDefenderFirst[(attacker, defender)] * chanceDefenderStarts
        if not (attacker, defender) in dNew:
          dNew[(attacker, defender)] = p
        else:
          dNew[(attacker, defender)] += p
      return dNew

  def winProbability(self, defender, chanceDefenderStarts = None, precise=True, maxError = 0.001):
    d = {(self, defender): 1.0}
    if not chanceDefenderStarts is None:
      d = Combatant.randomizeInitialAttacker(d, chanceDefenderStarts, precise=precise)

    undecidedCond = lambda attacker, defender: attacker.canFight() and defender.canFight()
    while Combatant.eventProbability(d, undecidedCond) > maxError:
      d = Combatant._applyAttackRound(d, precise=precise)

    winCond = lambda attacker, defender: defender.cantFight()
    return Combatant.eventProbability(d, winCond)


class DndCombatant(Combatant):
  def __init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, ac, damageDensity = None):
    if damageDensity is None:
      damageDensity = Combatant.dndDamageDensity
    Combatant.__init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, ac, damageDensity = damageDensity)


class Dnd2NealCombatant(DndCombatant):
  def __init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, ac):
    def nealDamageDensity(attacker, defender, attackRoll):
      if attackRoll == 1:
        return Zero()
      if (attackRoll + attacker.bonusToHit) < defender.evade and attackRoll < 20:
        return Zero()

      if attackRoll >= 18:
        criticalHits = max(0, math.floor((attackRoll + attacker.bonusToHit - defender.evade) / 5))
      else:
        criticalHits = max(0, math.floor((attackRoll + attacker.bonusToHit - defender.evade) / 10))
      criticalHits = min(3, criticalHits)

      criticalHitDamage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage))
      return criticalHitDamage
    DndCombatant.__init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, ac, damageDensity = nealDamageDensity)
