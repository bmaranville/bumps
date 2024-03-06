from bumps.names import *

def fn(x, a, b): return (a+b)*x

sigma = 1
x = np.linspace(-1., 1, 40)
dy = sigma*np.ones_like(x)
y = fn(x,5,5) + np.random.randn(*x.shape)*dy

M = Curve(fn, x, y, dy, a=(-20,20), b=(-20,20))

S = Parameter((-20,20), name="sum")
M.b = S-M.a

problem = FitProblem(M)


