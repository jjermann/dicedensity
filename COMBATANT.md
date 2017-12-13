// Copyright (C) 2017 by Jonas Jermann <jjermann2@gmail.com>

# Combatant module

An extension module to densities to simulate (specific) combats.


## Documentation:
### Combatant
A class that contains all relevant combat parameters for a combatant.
Combatant can also be used for DND-like combats (see `DND settings` remarks).
A combatant has the following properties:

* **`hp`**  
  The HP of the combatant (an integer or float).
  Each hit decreases HP by the amount of (expected) final damage dealt.
  If `hp` reaches 0 or below the combatant is considered dead.

* **`exhausts`**  
  The amount of exhaust points of the combatant (an integer).
  Each hit decreases exhausts by 1.
  If `exhausts` reaches 0 or below the combatant is considered unconscious (unless he is dead).

  :warning: (DND settings)  
  By default `exhausts = None` which corresponds to the DND system
  (in this case exhausts isn't considered at all and in particular the combatant can only be dead or unconscious).

* **`attackDie`**  
  The density that is used by the attacker to check if he hits the defender.
  For example `attackDie = ad20`.

* **`bonusToHit`**  
  A bonus value (an integer) that is added to the `attackDie` result at the end.

* **`damageDie`**  
  The density that is used by the attacker to deal damage to the defender.
  For example `damageDie = d8`.

* **`bonusToDamage`**  
  A bonus value (an integer) that is added to the `damageDie` result at the
  The bonus value is only added once in case of critical hits.

* **`evade`**  
  The evade value of the combatant (an integer).
  Another combatant has to reach at least this value with `attackDie` to be able to hit the combatant.

  :warning: (DND settings)  
  For DND `evade` is the same as `AC`.

* **`armor`**  
  The armor (integer) of the combatant.
  If an attacker hits the combatant but with an `attackDie` result of less than `evade + armor`
  then the `resistance` of the combatant is subtracted from the `damageDie` result of the attacker.

  :warning: (DND settings)  
  By default `armor = 0` which corresponds to the DND system.

* **`resistance`**  
  The amount by which the `damageDie` result of an attacker that hits armor is reduced (see `armor`).

  :warning: (DND settings)  
  By default `resistance = 0` which corresponds to the DND system.

Example:
```python3
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
      evade         = 5      ,\
      armor         = 10     ,\
      resistance    = 6       \
    )
```

DND example:
```python3
    combatantDnd = Combatant( \
      hp            = 20     ,\
      attackDie     = d20    ,\
      bonusToHit    = 1      ,\
      damageDie     = d8     ,\
      bonusToDamage = 3      ,\
      evade         = 13      \
    )
```


### Combatant methods
The following methods are defined on a given density `d`:

* **`damageDensity(self, other, attackRoll)`**  
  The damage density of the combatant against another combatant the given attackRoll

  For example `combatant1.damageDensity(combatant2, 10)` gives the density
  for all possible damage results of combatant1 with an attack roll of 10 against combatant2.

  :warning:  
  `isinstance(damageDensity, Zero)` can be used to check if `combatant1` has hit `combatant2` at all.

* **`chanceToHit(self, other)`**  
  The chance to hit another combatant

  :warning:  
  Note that it can also occur that a hit does 0 damage.
  In that case the defender still loses an exhaust value.

* **`expectedDamage(self, other)`**  
  The expected damage against another combatant

* **`plotDamage(self, other)`**  
  Plots the expected damage against another combatant parametrized by possible attack rolls (from `attackDie`).
  The expected overall damage and the chance to hit is also printed.

  Example:
  ```python3
    print(combatant1.plotDamage(combatant2))
  ```

* **`plotDamageImage(self, other)`**  
  Saves the expected damage (see `plotDamage`) as an image with name `ExpectedDamage.png`.

* **`isDead(self)`**  
  Returns whether the combatant is dead, i.e. whether `hp <= 0`

* **`isUnconscious(self)`**  
  Returns whether the combatant is unconscious, i.e. whether `exhausts <= 0` and `hp > 0`

* **`canFight(self)`**  
  Returns whether the combatant can fight, i.e. whether he is neither dead nor unconscious

* **`cantFight(self)`**  
  Returns whether the combatant is unable to fight, i.e. whether he is dead or unconscious

* **`Combatant.combatDistribution(attacker, defender, rounds = 1)`**  
  Determines all possible combat end results after the given number of `rounds` together with their probabilities.
  A result is a tuple (attacker, defender). The method returns a dictionary of all possible results as keys and the corresponding probabilities as values.
  The result dictionary can then be used again for further calculations...

  A combat round consists of the attacker attacking the defender followed by the defender attacking the attacker.
  If a combatant can't fight (i.e. if `combatant.cantFight()` is true) he doesn't hit and doesn't deal any damage anymore.
  Note that with each steps the possibilities of possible results increases.

  Example (will be used below):
  ```python3
    d = Combatant.combatDistribution(combatant1, combatant2, rounds=5)
  ```

* **`Combatant.eventProbability(d, cond)`**  
  Returns the probability of a specified event/condition `cond` for a given combat distribution `d`.
  `cond(attacker, defender)` has to be a Boolean function that selects events
  and `d` has to be a combat distribution as returned by `Combat.combatDistribution(...)`.

  Example:
  ```python3
    fightUndecidedCondition = lambda attacker, defender: attacker.canFight() and defender.canFight()
    fightUndecidedProbability = Combatant.eventProbability(d, fightUndecidedCondition)
    print(fightUndecidedCondition)
  ```

* **`Combatant.combatEventProbability(attacker, defender, cond, rounds = 1)`**  
  Returns the probability of a specified event/condition `cond` after the specified amount of
  `rounds` of combat between the given `attacker` and `defender` (both `Combatant`).
  This is the same as calculating `d = Combatant.combatDistribution(attacker, defender, rounds)`
  and then calculating `p = Combatant.eventProbability(d, cond)`.

  Example:
  ```python3
    attackerWinCondition = lambda attacker, defender: defender.cantFight()
    attackerWinProbabilityAfter5Rounds = Combatant.combatEventProbability(combatant1, combatant2, attackerWinCondition, rounds = 5)
    print(attackerWinProbabilityAfter5Rounds)
  ```

* **`Combatant.resultDensity(d, op)`**  
  For a given combat distribution `d` as returned by `Combatant.combatDistribution(...)`
  and a function `op(attacker, defender)` this method returns the `Density` over all possible results of `op`.

  For example if `attackerHpFunction = lambda attacker, defender: attacker.hp` then
  `Combatant.resultDensity(d, attackerHpFunction)` returns all a density
  over all possible attacker HP values for the combat distribution `d`
  with probabilities determined by `d`:

  ```python3
    attackerHpFunction = lambda attacker, defender: attacker.hp
    print(Combatant.resultDensity(d, attackerHpFunction))
  ```

* **`Combatant.combatResultDensity(attacker, defender, op, rounds = 1)`**  
  Returns the Density over all possible results of `op(attacker, defender)`
  after a specified amount of `rounds` of combat between the given `attacker` and `defender`.
  This is the same as calculating `d = Combatant.combatDistribution(attacker, defender, rounds)`
  and then calculating `p = Combatant.resultDensity(d, op)`.

  Example:
  ```python3
    attackerMoreHealthyThanDefender = lambda attacker, defender: attacker.hp > defender.hp
    attackerHealthierThanDefenderDensity = Combatant.combatResultDensity(combatant1, combatant2, attackerMoreHealthyThanDefender, rounds=1)
    print(attackerHealthierThanDefenderDensity)

    attackerPositiveHp = lambda attacker, defender: max(0, attacker.hp)
    attackerPositiveHpDensity = Combatant.combatResultDensity(combatant1, combatant2, attackerPositiveHp, rounds=5)
    print(attackerPositiveHpDensity)
  ```

* **`hpDensity(self, defender, rounds = 1)`**  
  Returns the density of the possible HPs of the combatant after the specified amount of `rounds` of combat against the specified `defender`.

  Example:
  ```python3
    print(combatant1.hpDensity(combatant2, rounds = 5))
  ```

* **`winProbability(self, defender, maxError = 0.001)`**  
  Returns the probability that the combatant wins against the specified `defender` within the specified margin of error `maxError`.

  :warning:  
  Smaller values of `maxError` lead to slower calculations of the result.

  Example:
  ```python3
    print(combatant1.winProbability(combatant2))
  ```
