from bumps.names import *

def line(x, m, b):
    return m*x + b

x = [1, 2, 3, 4, 5, 6]
y = [2.1, 4.0, 6.3, 8.03, 9.6, 11.9]
dy = [0.05, 0.05, 0.2, 0.05, 0.2, 0.2]

M = Curve(line, x, y, dy, m=2, b=0)
M.m.range(0, 4)
M.b.range(0, 5)

def constraints():
    m, b = M.m.value, M.b.value
    return 0 if m < b else 1e6 + (m-b)**6

problem = FitProblem(M, constraints=constraints, soft_limit=1e6)

