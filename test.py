from z3 import *

x = Bool("x")
y = Bool("y")
z = Bool("z")
cnf = And(Or(Not(x), y), Or(Not(y), z), x)

solver = Solver()
solver.add(cnf)
solver.check()

print(solver.model())
