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

  def damageDensity(self, other, attackRoll):
    if (attackRoll + self.bonusToHit) < other.evade:
      return Zero()

    if attackRoll + self.bonusToHit < other.evade + other.armor:
      armorHitDamage = self.damageDie.op(lambda a: max(0, a + self.bonusToDamage - other.resistance))
      return armorHitDamage

    criticalHits = math.floor(((attackRoll + self.bonusToHit) - (other.evade + other.armor)) / 5)
    criticalHitDamage = self.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + self.bonusToDamage))
    return criticalHitDamage

  def expectedDamage(self, other):
    return sum([self.attackDie[k]*self.damageDensity(other, k).expected() for k in self.attackDie.keys()])

  def plotDamage(self, other):
    res = ""
    res += "{:>12}\t{:>12.5f}".format("Expected", self.expectedDamage(other)) + "\n\n"
    res += get_plot(lambda k: self.damageDensity(other, k).expected(), self.attackDie.keys())
    return res

  def plotDamageImage(self, other):
    def ExpectedDamage(attackRoll):
      return self.damageDensity(other, attackRoll).expected()
    inputs = self.attackDie.keys()
    xlabel = "Attack roll (Total expected damage: {})".format(self.expectedDamage(other))
    ylabel = "Expected damage"
    plot_image(ExpectedDamage, inputs = inputs, xlabel=xlabel, ylabel=ylabel)

