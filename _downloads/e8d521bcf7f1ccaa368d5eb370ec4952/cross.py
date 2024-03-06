from bumps.names import *

scale = 10
sigma = 0.1*scale
#sigma = 0.001*scale  # Too small
#sigma = 10*scale   # Too large

def fn(a, b):
    return 0.5*min(abs(a+b),abs(a-b))**2/sigma**2 + 1

M = PDF(fn, a=3*scale, b=1.2*scale)

M.a.range(-3*scale,3*scale)
M.b.range(-1*scale,3*scale)

problem = FitProblem(M)


