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

* **`maxFatigue`**  
  The maximal amount of fatigue points (an integer) the combatant can endure before he becomes unconscious.

  :warning: (DND settings)  
  By default `maxFatigue = None` which corresponds to the DND system
  (in this case fatigue isn't considered at all and in particular the combatant can't become unconscious, just dead).

* **`fatigue`**  
  The amount of fatigue points of the combatant (an integer, default: 0).
  Each hit increases fatigue by 1 (unless `maxFatigue` is `None`).
  If `fatigue` reaches `maxFatigue` the combatant is considered unconscious (unless he is dead).

* **`attackDie`**  
  The density that is used by the attacker to check if he hits the defender.
  For example `attackDie = ad20`.

* **`bonusToHit`**  
  A bonus value (an integer) that is added to the `attackDie` result at the end.

* **`bonusToHitUnarmored`**  
  It depends on the damage density if this value is used (ignored for default).
  It's intended to be used as an (alternative) to `bonusToHit` in case the defender is not armored.

* **`damageDie`**  
  The density that is used by the attacker to deal damage to the defender.
  For example `damageDie = d8`.

* **`bonusToDamage`**  
  A bonus value (an integer) that is added to the `damageDie` result at the
  The bonus value is only added once in case of critical hits.

* **`criticalThreshold`**
  It depends on the damage density if this value is used (applied for default).
  Each damage excess in the amount of `criticalThreshold` leads to an additional/initial critical hit.
  If `criticalThreshold = None` no critical damage is applied (default: 5).

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
      maxFatigue    = 10     ,\
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
      maxFatigue    = 10     ,\
      attackDie     = d20    ,\
      bonusToHit    = 1      ,\
      damageDie     = d8     ,\
      bonusToDamage = -1     ,\
      evade         = 5      ,\
      armor         = 10     ,\
      resistance    = 6       \
    )
```


### DndCombatant
A subclass of `Combatant` with settings more suited for DND-like systems,
without `maxFatigue`, `fatigue`, `armor`, `resistance` and with `damageDensity = Combatant.dndDamageDensity`
(see below for more information) by default.

Example:
```python3
    dndCombatant = DndCombatant( \
      hp            = 20        ,\
      attackDie     = d20       ,\
      bonusToHit    = 1         ,\
      damageDie     = d8        ,\
      bonusToDamage = 3         ,\
      ac            = 13         \
    )
```


### Dnd2NealCombatant
A subclass of `DndCombatant` according to the combat rules of _2.Neal_ from http://regalgoblins.com/toolbox.php.

Example:
```python3
    nealCombatant = Dnd2NealCombatant( \
      hp            = 20              ,\
      attackDie     = ad20            ,\
      bonusToHit    = 9               ,\
      damageDie     = d8+d4           ,\
      bonusToDamage = 3               ,\
      ac            = 13               \
    )
```


### Combatant methods
The following methods are defined on a given density `d`:

* **`damageDensity(self, defender, attackRoll)`**  
  The damage density of the combatant against another combatant the given attackRoll

  For example `combatant1.damageDensity(combatant2, 10)` gives the density
  for all possible damage results of combatant1 with an attack roll of 10 against combatant2.

  :warning:  
  `isinstance(damageDensity, Zero)` can be used to check if `combatant1` has hit `combatant2` at all.

* **`chanceToHit(self, defender)`**  
  The chance to hit another combatant

  :warning:  
  Note that it can also occur that a hit does 0 damage.
  In that case the defender still gains a fatigue value.

* **`expectedDamage(self, defender)`**  
  The expected damage against another combatant

* **`plotDamage(self, defender)`**  
  Plots the expected damage against another combatant parametrized by possible attack rolls (from `attackDie`).
  The expected overall damage and the chance to hit is also printed.

  Example:
  ```python3
    print(combatant1.plotDamage(combatant2))
  ```

* **`plotDamageImage(self, defender)`**  
  Saves the expected damage (see `plotDamage`) as an image with name `ExpectedDamage.png`.

* **`isDead(self)`**  
  Returns whether the combatant is dead, i.e. whether `hp <= 0`

* **`isUnconscious(self)`**  
  Returns whether the combatant is unconscious, i.e. whether `fatigue >= maxFatigue` and `hp > 0`

* **`canFight(self)`**  
  Returns whether the combatant can fight, i.e. whether he is neither dead nor unconscious

* **`cantFight(self)`**  
  Returns whether the combatant is unable to fight, i.e. whether he is dead or unconscious


### Combatant methods regarding combat distributions
There are various methods to simulate combats.
If `precise=False` then the expected damage is used instead of aggregating all possible damage
results, this makes the calculations *significantly faster* (around 100 times).
If `simple=True` then it is assumed that the damage density remains the same for attacker and defender during the whole combat,
this makes the calculations *significantly faster* as well but for instance doesn't consider exhaustion effects.

* **`damageDensityDistribution(self, defender)`**
  Returns all possible damage densities against the specified defender together with the respective probability as a distribution.

* **`Combatant.combatDistribution(attacker, defender, rounds = 1, chanceDefenderStarts = None, precise = True, simple = False)`**  
  Determines all possible combat end results after the given number of `rounds` together with their probabilities.
  If `chanceDefenderStarts` is specified then the defender has the specified chance to attack beforehand.
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).
  If `simple=True` is specified then always the initial damage density distribution is used for the attacker and defender
  (significantly faster but doesn't reflect changed attacker or defender conditions).

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

* **`Combatant.combatEventProbability(attacker, defender, cond, rounds = 1, chanceDefenderStarts = None, precise = True, simple = False)`**  
  Returns the probability of a specified event/condition `cond` after the specified amount of
  `rounds` of combat between the given `attacker` and `defender` (both `Combatant`).
  If `chanceDefenderStarts` is specified then the defender has the specified chance to attack beforehand.
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).
  If `simple=True` is specified then always the initial damage density distribution is used for the attacker and defender
  (significantly faster but doesn't reflect changed attacker or defender conditions).
  This is the same as calculating `d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise, simple)`
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

* **`Combatant.combatResultDensity(attacker, defender, op, rounds = 1, chanceDefenderStarts = None, precise = True, simple = False)`**  
  Returns the Density over all possible results of `op(attacker, defender)`
  after a specified amount of `rounds` of combat between the given `attacker` and `defender`.
  If `chanceDefenderStarts` is specified then the defender has the specified chance to attack beforehand.
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).
  If `simple=True` is specified then always the initial damage density distribution is used for the attacker and defender
  (significantly faster but doesn't reflect changed attacker or defender conditions).
  This is the same as calculating `d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise, simple)`
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

* **`Combatant.randomizeInitialAttacker(d, chanceDefenderStarts = 0.5, precise = True)`**  
  Returns a new distribution where the defender gets an initial attack in first according to the specified percentage `chanceDefenderStarts`.
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).

  Example:
  ```python3
    d = Combatant.combatDistribution(combatant1, combatant2, rounds=5)
    dRandomizedStart = Combatant.randomizeInitialAttacker(d, 0.5)
    print(dRandomizedStart)
  ```

* **`hpDensity(self, defender, rounds = 1, chanceDefenderStarts = None, precise = True, simple = False)`**  
  Returns the density of the possible HPs of the combatant after the specified amount of `rounds` of combat against the specified `defender`.
  If `chanceDefenderStarts` is specified then the defender has the specified chance to attack beforehand.
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).
  If `simple=True` is specified then always the initial damage density distribution is used for the attacker and defender
  (significantly faster but doesn't reflect changed attacker or defender conditions).
  This is the same as calculating `d = Combatant.combatDistribution(attacker, defender, rounds, chanceDefenderStarts, precise, simple)`

  Example:
  ```python3
    print(combatant1.hpDensity(combatant2, rounds = 5))
  ```

* **`winProbability(self, defender, chanceDefenderStarts = None, precise = True, simple = False, maxError = 0.05, includeError = False)`**  
  Returns the probability that the combatant wins against the specified `defender` within the specified margin of error `maxError`.
  If `chanceDefenderStarts` is not specified then the attacker always starts.
  Otherwise the defender gets an initial attack according to the specified percentage
  (after that combatants always take turns as usual).
  If `precise=False` is specified then the expected damage is used for damage calculations (significantly faster but less precise end result).
  If `simple=True` is specified then always the initial damage density distribution is used for the attacker and defender
  (significantly faster but doesn't reflect changed attacker or defender conditions).
  If `includeError=True` is specified then a tuple `(p, minP, error)` is returned instead,
  where `p` is the estimated probability, `minP` is a lower bound and `error` is an upper bound on the error.

  :warning:
  Smaller values of `maxError` lead to slower calculations of the result.

  Example:
  ```python3
    print(combatant1.winProbability(combatant2))
    print(combatant1.winProbability(combatant2, chanceDefenderStarts = 0.5))
  ```

* **`simpleWinProbability(self, defender, chanceDefenderStarts = 0.5, maxError = 0.001, includeError = False)`**
  Returns the probability that the combatant wins against the specified `defender` using simplifications for increased performance.
  The arguments are the same as for `winProbability`.
  This is the same as calculating `p = self.winProbability(defender, chanceDefenderStarts = chanceDefenderStarts, precise = False, simple = True, maxError = maxError)`.

  Example:
  ```python3
    print(combatant1.simpleWinProbability(combatant2))


### More general damage densities
It is possible to specify alternative damage densities for combatant.
The damage density specifies the damage density for the damage dealt by an
`attacker` to a `defender` given the attacker rolled `attackRoll`.
The more genral damage density can be specified with the parameter `damageDensity`.

Example:
```python3
    def dndDamageDensity(attacker, defender, attackRoll):
      minValue = min(attacker.attackDie.values())
      maxValue = max(attacker.attackDie.values())
      if attackRoll == minValue:
        return Zero()
      if (attackRoll + attacker.bonusToHit) < defender.evade and attackRoll < maxValue:
        return Zero()

      criticalHits = 1 if attackRoll == maxValue 0 else
      damage = attacker.damageDie.arithMult(1 + criticalHits).op(lambda a: max(0, a + attacker.bonusToDamage))
      return damage
    dndCombatant = Combatant( \
      hp            = 20     ,\
      attackDie     = d20    ,\
      bonusToHit    = 1      ,\
      damageDie     = d8     ,\
      bonusToDamage = 3      ,\
      evade         = 13     ,\
      damageDensity = dndDamageDensity\
    )
```

By default the damage density for `Combatant` is set to `Combatant.defaultDamageDensity`.
The damage density from the example above is also available in `Combatant.dndDamageDensity`
and is the default damage density for `DndCombatant`.

Example:
```python3
    dndCombatant = Combatant( \
      hp            = 20     ,\
      attackDie     = d20    ,\
      bonusToHit    = 1      ,\
      damageDie     = d8     ,\
      bonusToDamage = 3      ,\
      evade         = 13     ,\
      damageDensity = Combatant.dndDamageDensity\
    )
```

:warning:  
Note that the logic when `fatigue` is increased (assuming `maxFatigue` is not `None`) still remains the same (on a hit).
