import ast
import operator as op
import re
import math
import heapq
from itertools import product
from functools import reduce

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.USub: op.neg,
             ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge}

def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
  if isinstance(node, ast.Num):
    return Constant(node.n)
  elif isinstance(node, ast.Name):
    nodeStr = node.id
    match = re.search(r'(m(\d*))?([ad]?)d(\d+)', nodeStr)
    if match is None:
      raise TypeError(node)
    else:
      if match.group(2):
        nr = int(match.group(2))
      else:
        nr = 1
      die = int(match.group(4))
      if match.group(3) == "a":
        resDensity = AdvantageDie(die)
      elif match.group(3) == "d":
        resDensity = DisadvantageDie(die)
      else:
        resDensity = Die(die)
      return resDensity.arithMult(nr)
  elif isinstance(node, ast.BinOp):
      return operators[type(node.op)](eval_(node.left), eval_(node.right))
  elif isinstance(node, ast.UnaryOp):
      return operators[type(node.op)](eval_(node.operand))
  elif isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
      return operators[type(node.ops[0])](eval_(node.left), eval_(node.comparators[0]))
  else:
      raise TypeError(node)

def getDensity(arg):
  if isinstance(arg, (int, float)):
    return Constant(arg)

  if isinstance(arg, Density):
    return arg
  else:
    raise ValueError("arg must be a Density or a number!")

          
class Density:
  def __init__(self, densities):
    if isinstance(densities, dict):
      self.densities = densities
    else:
      raise ValueError("densities must be a density dictionary")

  def _plotBar(self, key, width=70):
    maxPerc = max(self.densities.values())
    p = self.densities[key]
    numberOfBars = int(round(p*width*1.0/maxPerc))
    plotRes = ""
    for k in range(1, numberOfBars+1):
        plotRes += "█"
    return plotRes

  def __str__(self):
    s = ""
    if not self.isValid():
      s += "Invalid Density!\n"
    s += "{:>12}\t{:>12.5f}".format("Expected", self.expected()) + "\n"
    s += "{:>12}\t{:>12.5f}".format("Stdev", self.stdev()) + "\n"
    s += "\n"
    s += "{:>12}\t{:>12}\t{}".format("Result", "Probability", "Plot") + "\n"
    for dKey in sorted(self.densities):
      prob = self.densities[dKey]
      if prob > 0:
        s += "{:>12}\t{:>12.4%}".format(dKey, prob)
        s += "\t" + self._plotBar(dKey, 40)
        s += "\n"
    return s
 
  def isValid(self):
    return abs(1.0 - sum(self.densities.values())) < 1e-09

  def arithMult(self, other):
    if isinstance(other, (int)) and other >= 0:
      if other == 0:
        return Zero()
      else:
        res = self
        for i in range(other-1):
          res += self
        return res
    else:
      raise ValueError("other must be a nonnegative int!")

  def asMultiDensity(self, n):
    densityList = [self] * n
    return MultiDensity(*densityList)

  def binOp(self, other, opr):
    otherDensity = getDensity(other)
    resDensity = {}
    for sKey in self.densities.keys():
      for oKey in otherDensity.densities.keys():
        resKey = opr(sKey, oKey)
        if resKey not in resDensity:
          resDensity[resKey] = 0.0
        resDensity[resKey] += 1.0*self.densities[sKey]*otherDensity.densities[oKey]
    return Density(resDensity)

  def __add__(self, other):
    return self.binOp(other, lambda a,b : a+b)

  def __sub__(self, other):
    return self + (-other)
  
  def __mul__(self, other):
    return self.binOp(other, lambda a,b: a*b)

  __radd__ = __add__
  __rsub__ = __sub__
  __rmul__ = __mul__

  def op(self, opr):
    densities = {}
    for key in self.densities.keys():
      opKey = opr(key)
      if opKey not in densities:
        densities[opKey] = 0.0
      densities[opKey] += self.densities[key]
    return Density(densities)

  def __neg__(self):
    return self.op(lambda k: -k)

  def __abs__(self):
    return self.op(lambda k: abs(k))

  def prob(self, other, cond):
    otherDensity = getDensity(other)
    resSum = 0.0
    for sKey in self.densities.keys():
      for oKey in otherDensity.densities.keys():
        if cond(sKey, oKey):
          resSum += self.densities[sKey]*otherDensity.densities[oKey]
    return resSum

  def __eq__(self, y):
    return self.prob(y, lambda a,b: a == b)

  def __ne__(self, y):
    return self.prob(y, lambda a,b: a != b)

  def __lt__(self, y):
    return self.prob(y, lambda a,b: a < b)

  def __le__(self, y):
    return self.prob(y, lambda a,b: a <= b)

  def __gt__(self, y):
    return self.prob(y, lambda a,b: a > b)

  def __ge__(self, y):
    return self.prob(y, lambda a,b: a >= b)

  def conditionalDensity(self, cond):
    densities = {}
    for key in self.densities.keys():
      if cond(key):
        densities[key] = self.densities[key]
    condProb = sum(densities.values())
    for key in densities.keys():
      densities[key] /= condProb
    return Density(densities)

  def expected(self):
    resSum = 0.0
    for key in self.densities.keys():
      resSum += key*self.densities[key]
    return resSum

  def variance(self):
    resSum = 0.0
    expected = self.expected()
    for key in self.densities.keys():
      resSum += (key-expected)**2*self.densities[key]
    return resSum

  def stdev(self):
    return math.sqrt(self.variance())

  def plot(self, width=70):
    plotRes = "\n"

    for key in sorted(self.densities):
      plotRes += "{0:>12}\t".format(key)
      plotRes += self._plotBar(key, width)
      plotRes += "\n"
    return plotRes

  def with_advantage(self):
    return self.binOp(self, lambda a,b: max(a,b))

  def with_disadvantage(self):
    return self.binOp(self, lambda a,b: min(a,b))

  def summedDensity(self, goal):
    if min(self.densities.keys()) <= 0:
      raise ValueError("summedDensity only works with positive results!")

    densities = {}
    prevDensity = Zero()
    prevProb = 1
    prevKey = 0
 
    while (prevProb > 0):
      tDensity = prevDensity.conditionalDensity(lambda k: k <= goal) + self
      tProb = tDensity.prob(goal, lambda a,b: a > b)*prevProb
      if (tProb > 0):
        densities[prevKey] = tProb
 
      prevDensity += self
      prevProb = prevDensity.prob(goal, lambda a,b: a <= b)
      prevKey += 1
   
    return Density(densities)
 

class Die(Density):
  def __init__(self, die):
    densities = {}
    for r in range(1, die+1):
      densities[r] = 1.0 / die
    Density.__init__(self, densities)
 
class Constant(Density):
  def __init__(self, const):
    densities = {const:1.0}
    Density.__init__(self, densities)
 
class Zero(Constant):
  def __init__(self):
    Constant.__init__(self, 0)

def AdvantageDie(die):
  return Die(die).with_advantage()

def DisadvantageDie(die):
  return Die(die).with_disadvantage()

def DieExpr(expr):
  return eval_expr(expr)
  
class MultiDensity(Density):
  def __init__(self, *dList):
    self.densityList = dList
    Density.__init__(self, sum(self.densityList).densities)

  def multiOp(self, opr):
    dList = map(lambda k: map(lambda l: [l, k.densities[l]], k.densities.keys()), self.densityList)
    resDensity = {}
    for p in product(*dList):
      resKey = opr(*list(map(lambda k: k[0], p)))
      if resKey not in resDensity:
        resDensity[resKey] = 0.0
      summand = reduce(op.mul, map(lambda k: k[1], p), 1.0)
      resDensity[resKey] += summand
    return Density(resDensity)

  def drop_highest(self, n=1):
    if n == 1:
      return self.multiOp(lambda *a: sum(a)-max(a))
    else:
      return self.multiOp(lambda *a: sum(a)-sum(heapq.nlargest(n,a)))

  def drop_lowest(self, n=1):
    if n == 1:
      return self.multiOp(lambda *a: sum(a)-min(a))
    else:
      return self.multiOp(lambda *a: sum(a)-sum(heapq.nsmallest(n,a)))
