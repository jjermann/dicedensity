import ast
import operator as op
import re
import math
import heapq
import matplotlib.pyplot as plt
from itertools import product
from functools import reduce
from statistics import median

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

def plot_line(p, minP, maxP, plotWidth):
  aboveMax = p - maxP > 1e-9
  belowMin = minP - p > 1e-9

  p = max(p, minP)
  p = min(p, maxP)
  filledWidth = int(round(1.0*(p-minP)*plotWidth/(maxP-minP)))
  zeroPosition = int(round(1.0*(-minP)*plotWidth/(maxP-minP)))

  mainContent = filledWidth*'█' + (plotWidth-filledWidth)*' '
  if zeroPosition > 0 and zeroPosition < plotWidth:
    mainContent = mainContent[:zeroPosition] + '│' + mainContent[zeroPosition + 1:]

  if belowMin:
    result = '│'
  else:
    result = '█'
  result += mainContent
  if aboveMax:
    result += '█'
  else:
    result += '│'
  return result

def centered_plot_line(p, minP, maxP, plotWidth):
  aboveMax = p - maxP > 1e-9
  belowMin = minP - p > 1e-9

  p = max(p, minP)
  p = min(p, maxP)
  filledWidth = int(round(1.0*abs(p)*plotWidth/(maxP-minP)))
  zeroPosition = int(round(1.0*(-minP)*plotWidth/(maxP-minP)))

  mainContent = plotWidth*' '
  if p >= 0:
    mainContent = mainContent[:zeroPosition] + filledWidth*'█' + mainContent[zeroPosition + filledWidth:]
  else:
    mainContent = mainContent[:zeroPosition - filledWidth] + filledWidth*'█' + mainContent[zeroPosition:]

  if zeroPosition > 0 and zeroPosition < plotWidth:
    mainContent = mainContent[:zeroPosition] + '│' + mainContent[zeroPosition + 1:]

  if belowMin:
    result = '█'
  else:
    result = '│'
  result += mainContent
  if aboveMax:
    result += '█'
  else:
    result += '│'
  return result

def get_plot(p, inputs = range(-20, 20 + 1), plotWidth = 50, minP = None, maxP = None, asPercentage = False, centered = True):
  if minP is None:
    minP = min(0, min([p(k) for k in inputs]))
  if maxP is None:
    maxP = max([p(k) for k in inputs])
  if asPercentage:
    formatString = "{0:>12}\t{1:>12.2%}\t{2}"
  else:
    formatString = "{0:>12}\t{1:>12}\t{2}"
  if centered:
    plotFunction = centered_plot_line
  else:
    plotFunction = plot_line

  return str.join("\n",list(map(lambda k:\
    formatString.format(\
      round(k,4),\
      round(p(k), 4),\
      plotFunction(p(k),minP,maxP,plotWidth)\
    ), inputs)))

def get_simple_plot(p, inputs = range(-20, 20 + 1), plotWidth = 50, minP = None, maxP = None, asPercentage = False, centered = True):
  if asPercentage:
    formatString = "{0:.2%}"
  else:
    formatString = "{0}"
  return str.join("\n",list(map(lambda k:\
    formatString.format(round(p(k), 4)),\
    inputs)))

def plot_image(p, inputs = range(-20, 20 + 1), name = "plot", xlabel = "Input", ylabel = "Output"):
  fig = plt.figure()
  plt.plot(inputs, [p(k) for k in inputs])
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.title(name)
  #plt.show()
  plt.savefig(name)

def gaussMap(mu=0.0, stdev=1.0):
  return lambda x: 1.0/math.sqrt(2*math.pi*stdev**2)*math.exp(-(x-mu)**2/(2.0*stdev**2))

class Density:
  def __init__(self, densities):
    self._cdfList = None
    if isinstance(densities, dict):
      self.densities = densities
    else:
      raise ValueError("densities must be a density dictionary")

  def __str__(self):
    s = ""
    if not self.isValid():
      s += "Invalid Density!\n"
    s += "{:>12}\t{:>12.5f}".format("Expected", self.expected()) + "\n"
    s += "{:>12}\t{:>12.5f}".format("Stdev", self.stdev()) + "\n"
    s += "\n"
    s += "{:>12}\t{:>12}\t{}".format("Result", "Probability", "Plot") + "\n"
    s += self.plot(50)
    return s

  def __repr__(self):
    return self.__str__()

  def keys(self):
    return sorted(self.densities.keys())

  def values(self):
    return [ self.densities[k] for k in self.keys() ]

  def isValid(self):
    return abs(1.0 - sum(self.values())) < 1e-09

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
    for sKey in self.keys():
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
    for key in self.keys():
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
    for sKey in self.keys():
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
    for key in self.keys():
      if cond(key):
        densities[key] = self.densities[key]
    condProb = sum(densities.values())
    for key in densities.keys():
      densities[key] /= condProb
    return Density(densities)

  def expected(self):
    resSum = 0.0
    for key in self.keys():
      resSum += key*self.densities[key]
    return resSum

  def variance(self):
    resSum = 0.0
    expected = self.expected()
    for key in self.keys():
      resSum += (key-expected)**2*self.densities[key]
    return resSum

  def stdev(self):
    return math.sqrt(self.variance())

  def cdf(self, x):
    return self <= x;

  def _getCdfList(self):
    if self._cdfList is None:
      self._cdfList = [ [k,self.cdf(k)] for k in sorted(self.keys()) ]
    return self._cdfList

  def inverseCdf(self, p):
    if p < 0.0 or p > 1.0:
      raise ValueError("Argument must be a probability (0<=p<=1)!")
    for it in self._getCdfList():
      if it[1] >= p:
        return it[0]
    return self._getCdfList()[-1][0]

  def median(self):
    sortedKeys = sorted(self.keys())
    el = self.inverseCdf(0.5)
    elIndex = sortedKeys.index(el)
    if (self.cdf(el) - 0.5) < 1e-9:
      candidates = [ it[0] for it in self._getCdfList() if abs(it[1]-0.5) < 1e-9 ]
      return median(candidates)
    else:
      if elIndex == 0:
        return el
      else:
        elPrev = sortedKeys[elIndex-1]
        return (el + elPrev)/2.0

  def normalApproximation(self, x):
    return gaussMap(self.expected(), self.stdev())(x)

  def plot(self, plotWidth=70):
    maxPerc = max(self.values())
    return get_plot(lambda k: self.densities[k], self.keys(), plotWidth=plotWidth, minP=0.0, maxP=maxPerc, asPercentage=True)

  def plotImage(self, name="plot"):
    plot_image(lambda k: self.densities[k], self.keys(), name = name, xlabel = "Result", ylabel = "Probability")

  def with_advantage(self):
    return self.binOp(self, lambda a,b: max(a,b))

  def with_disadvantage(self):
    return self.binOp(self, lambda a,b: min(a,b))

  def summedDensity(self, goal):
    if min(self.keys()) <= 0:
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
