
from densities import *

class Combatant:
  def __init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, evade, armor = 0, resistance = 0, maxFatigue = None, fatigue = 0, criticalThreshold = 5, damageDensity = None, bonusToHitUnarmored = None):
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
    self.criticalThreshold = criticalThreshold
    self.bonusToHitUnarmored = bonusToHitUnarmored
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
    return Combatant(self.hp, self.attackDie, self.bonusToHit, self.damageDie, self.bonusToDamage, self.evade, self.armor, self.resistance, self.maxFatigue, self.fatigue, self.criticalThreshold, self._damageDensity, self.bonusToHitUnarmored)

  @staticmethod
  def defaultDamageDensity(attacker, defender, attackRoll):
    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade:
      return Zero()

    if attackRoll + attacker.bonusToHit + attacker.fatigueModifier() < defender.evade + defender.armor:
      armorHitDamage = attacker.damageDie.op(lambda a: max(0, a + attacker.bonusToDamage - defender.resistance))
      return armorHitDamage

    if (attacker.criticalThreshold is None):
      criticalHits = 0
    else:
      criticalHits = math.floor(((attackRoll + attacker.bonusToHit + attacker.fatigueModifier()) - (defender.evade + defender.armor)) / attacker.criticalThreshold)
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

    if (attacker.criticalThreshold is None):
      criticalHits = 0
    else:
      criticalHits = math.floor(((attackRoll + attacker.bonusToHit + attacker.fatigueModifier()) - (defender.evade + defender.armor)) / attacker.criticalThreshold)
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

  def damageDensityDistribution(self, defender, cond=None):
    d = {}
    for k in self.attackDie.keys():
      damageDensity = self.damageDensity(defender, k)
      if cond is None or cond(damageDensity):
        try:
          d[damageDensity] += self.attackDie[k]
        except KeyError:
          d[damageDensity] = self.attackDie[k]
    if not cond is None:
      condProb = sum([p for p in d.values()])
      for k in d:
        d[k] /= condProb
    return d

  def chanceToHit(self, defender):
    d = self.damageDensityDistribution(defender)
    isHit = lambda damageDensity: not isinstance(damageDensity, Zero)
    chance = sum([d[damageDensity]*(1.0 if isHit(damageDensity) else 0.0) for damageDensity in d])
    return chance

  def expectedDamage(self, defender, cond=None):
    d = self.damageDensityDistribution(defender,cond)
    return sum([d[damageDensity]*damageDensity.expected() for damageDensity in d])

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

  def _attackedCombatantDistribution(self, defender, damageDensity):
    d = {}
    if (self.cantFight()):
      return {defender.clone(): 1.0}

    isHit = not isinstance(damageDensity, Zero)

    if not isHit:
      return {defender.clone(): 1.0}

    applyFatigue = isHit and not defender.maxFatigue is None and defender.fatigue < defender.maxFatigue
    d = {}
    for damage in damageDensity.keys():
      clone = defender.clone()
      clone.hp -= damage
      clone.hp = max(0, clone.hp)
      if applyFatigue:
        clone.fatigue += 1
      try:
        d[clone] += damageDensity[damage]
      except KeyError:
        d[clone] = damageDensity[damage]
    return d

  def _expectedAttackedCombatant(self, defender, damageDensity):
    if (self.cantFight()):
      return defender.clone()

    damage = damageDensity.expected()
    isHit = not isinstance(damageDensity, Zero)
    clone = defender.clone()
    clone.hp -= damage
    clone.hp = max(0, clone.hp)

    applyFatigue = isHit and not clone.maxFatigue is None and clone.fatigue < clone.maxFatigue
    if applyFatigue:
      clone.fatigue += 1
    return clone

  @staticmethod
  def _adjustedAttackDistribution(d, reversed=False, precise=True, simple=False, attackerDmgDist=None, defenderDmgDist=None):
    dNew = {}
    if reversed:
      if simple:
        dd = defenderDmgDist
      for (attacker, defender) in d:
        if not simple:
          dd = defender.damageDensityDistribution(attacker)
        for damageDensity in dd:
          if precise:
            attackerD = defender._attackedCombatantDistribution(attacker, damageDensity)
            for attackerNew in attackerD:
              try:
                dNew[(attackerNew, defender)] += dd[damageDensity]*d[(attacker, defender)]*attackerD[attackerNew]
              except KeyError:
                dNew[(attackerNew, defender)] = dd[damageDensity]*d[(attacker, defender)]*attackerD[attackerNew]
          else:
            attackerNew = defender._expectedAttackedCombatant(attacker, damageDensity)
            try:
              dNew[(attackerNew, defender)] += dd[damageDensity]*d[(attacker, defender)]
            except KeyError:
              dNew[(attackerNew, defender)] = dd[damageDensity]*d[(attacker, defender)]
    else:
      if simple:
        dd = attackerDmgDist
      for (attacker, defender) in d:
        if not simple:
          dd = attacker.damageDensityDistribution(defender)
        for damageDensity in dd:
          if precise:
            defenderD = attacker._attackedCombatantDistribution(defender, damageDensity)
            for defenderNew in defenderD:
              try:
                dNew[(attacker, defenderNew)] += dd[damageDensity]*d[(attacker, defender)]*defenderD[defenderNew]
              except KeyError:
                dNew[(attacker, defenderNew)] = dd[damageDensity]*d[(attacker, defender)]*defenderD[defenderNew]
          else:
            defenderNew = attacker._expectedAttackedCombatant(defender, damageDensity)
            try:
              dNew[(attacker, defenderNew)] += dd[damageDensity]*d[(attacker, defender)]
            except KeyError:
              dNew[(attacker, defenderNew)] = dd[damageDensity]*d[(attacker, defender)]
    return dNew

  @staticmethod
  def _applyAttackRound(d, precise=True, simple=False, attackerDmgDist=None, defenderDmgDist=None):
    dNew1 = Combatant._adjustedAttackDistribution(d, precise=precise, simple=simple, attackerDmgDist=attackerDmgDist, defenderDmgDist=defenderDmgDist)
    dNew2 = Combatant._adjustedAttackDistribution(dNew1, reversed=True, precise=precise, simple=simple, attackerDmgDist=attackerDmgDist, defenderDmgDist=defenderDmgDist)
    return dNew2

  @staticmethod
  def combatDistribution(attacker, defender, rounds = 1, chanceDefenderStarts = None, precise=True, simple=False):
    if simple:
      attackerDmgDist = attacker.damageDensityDistribution(defender)
      defenderDmgDist = defender.damageDensityDistribution(attacker)
    else:
      attackerDmgDist = None
      defenderDmgDist = None
    d = {(attacker, defender): 1.0}
    if not chanceDefenderStarts is None:
      d = Combatant.randomizeInitialAttacker(d, chanceDefenderStarts, precise=precise)

    for round in range(rounds):
      d = Combatant._applyAttackRound(d, precise=precise, simple=simple, attackerDmgDist=attackerDmgDist, defenderDmgDist=defenderDmgDist)
    return d

  @staticmethod
  def eventProbability(d, cond):
    return sum([d[(attacker, defender)] for (attacker, defender) in d if cond(attacker, defender)])

  @staticmethod
  def combatEventProbability(attacker, defender, cond, rounds = 1, chanceDefenderStarts = None, precise=True, simple=False):
    d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise=precise, simple=simple)
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
  def combatResultDensity(attacker, defender, op, rounds = 1, chanceDefenderStarts = None, precise=True, simple=False):
    d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise=precise, simple=simple)
    return Combatant.resultDensity(d, op)

  def hpDensity(self, defender, rounds = 1, chanceDefenderStarts = None, precise=True, simple=False):
    op = lambda attacker, defender: attacker.hp
    return Combatant.combatResultDensity(self, defender, op, rounds, chanceDefenderStarts, precise=precise, simple=simple)

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

  def winProbability(self, defender, chanceDefenderStarts = None, precise = True, simple = False, maxError = 0.005, includeError = False):
    if simple:
      attackerDmgDist = self.damageDensityDistribution(defender)
      defenderDmgDist = defender.damageDensityDistribution(self)
    else:
      attackerDmgDist = None
      defenderDmgDist = None
    d = {(self, defender): 1.0}
    if not chanceDefenderStarts is None:
      d = Combatant.randomizeInitialAttacker(d, chanceDefenderStarts, precise=precise)

    undecidedCond = lambda attacker, defender: attacker.canFight() and defender.canFight()
    while Combatant.eventProbability(d, undecidedCond) > maxError:
      d = Combatant._applyAttackRound(d, precise=precise, simple=simple, attackerDmgDist=attackerDmgDist, defenderDmgDist=defenderDmgDist)

    winCond = lambda attacker, defender: defender.cantFight()
    p = Combatant.eventProbability(d, winCond)
    up = Combatant.eventProbability(d, undecidedCond)

    if includeError:
      return (p + up*p/(1-up), p, up)

    return p + up*p/(1-up)

  def simpleWinProbability(self, defender, chanceDefenderStarts = 0.5, maxError = 0.001):
    p = self.winProbability(defender, chanceDefenderStarts = chanceDefenderStarts, precise = False, simple = True, maxError = maxError)
    return p


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

      criticalHitDamage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(1, a + attacker.bonusToDamage))
      return criticalHitDamage
    DndCombatant.__init__(self, hp, attackDie, bonusToHit, damageDie, bonusToDamage, ac, damageDensity = nealDamageDensity)

class DndNealTestCombatant(Combatant):
  def __init__(self, hp, bonusToHit, damageDie, bonusToDamage, evade, criticalThreshold, armor = 0, maxFatigue = None, bonusToHitUnarmored = None):
    if (bonusToHitUnarmored is None):
      bonusToHitUnarmored = bonusToHit

    def nealTestDensity(attacker, defender, attackRoll):
      armored = armor > 0
      bonusToHit = attacker.bonusToHit if armored else attacker.bonusToHitUnarmored
      excess = attackRoll + bonusToHit - defender.evade
      if (excess < 0):
        return Zero()

      if attacker.criticalThreshold is None:
        criticalHits = 0
      else:
        criticalHits = excess // attacker.criticalThreshold
      damage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage - defender.resistance))
      return damage
    Combatant.__init__(self, hp, d100, bonusToHit, damageDie, bonusToDamage, evade, resistance=armor, maxFatigue=maxFatigue, criticalThreshold=criticalThreshold, damageDensity = nealTestDensity, bonusToHitUnarmored = bonusToHitUnarmored)
