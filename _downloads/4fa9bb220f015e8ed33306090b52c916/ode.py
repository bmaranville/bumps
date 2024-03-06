from bumps.names import *
import numpy as np
from scipy.integrate import odeint

def g(t, x0, a, b):
    """
    Solution to the ODE x'(t) = f(t,x,k) with initial condition x(0) = x0
    """
    return odeint(dfdt, x0, t, args=(a, b)).flatten()

def dfdt(x, t, a, b):
    """Receptor synthesis-internalization model."""
    return a - b*x

def simulate():
    from bumps.util import push_seed

    # Fake some data
    a = 2.0
    b = 0.5
    x0 = 10.0
    t = np.linspace(0, 10, 10)
    dy = 0.2*np.ones_like(t)
    with push_seed(1):
        y = g(t, x0, a, b) + dy*np.random.normal(size=t.shape)
    #print(a, b, x0, t, dt, gt)
    return t, y, dy

t, y, dy = simulate()

M = Curve(g, t, y, dy, x0=1., a=1., b=1.,
          plot_x=np.linspace(t[0], t[-1], 1000))
M.x0.range(0, 100)
M.a.range(0, 10)
M.b.range(0, 10)

problem = FitProblem(M)


