#!/usr/bin/python3

from densities import *
import sys

if len(sys.argv) == 1:
  msg = "Syntax: {} <die expression>\n\n".format(sys.argv[0])
  msg += "Supported density operators (resulting in a density): +, -, *, abs()\n"
  msg += "Supported comparison operators (resulting in a probability): <, >, <=, >=, ==, !=\n"
  msg += "Syntax for densities: d<number> (normal die), ad<number> (advantage die), dd<number> (disadvantage die), <number> (constant density)\n"
  msg += "Remark: 3*d20 corresponds to one d20 who's result is multiplied by 3, m3d20 corresponds to d20+d20+d20\n\n"
  msg += "Example: d20 + d6, d20 + d6 == 7, ad20-d6"
  print(msg)
else:
  arguments = str.join("", sys.argv[1:])
  expr = DieExpr(arguments);
  if isinstance(expr, Density):
    print(expr)
  elif isinstance(expr, float):
    print("{:.4%}".format(expr))
