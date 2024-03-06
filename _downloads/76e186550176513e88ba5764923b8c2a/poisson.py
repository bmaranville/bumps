from bumps.names import *

def peak(x, scale, center, width, background):
    return scale*np.exp(-0.5*(x-center)**2/width**2) + background

x = np.linspace(5, 20, 345)
#y = np.random.poisson(peak(x, 1000, 12, 1.0, 1))
#y = np.random.poisson(peak(x, 300, 12, 1.5, 1))
y = np.random.poisson(peak(x, 3, 12, 1.5, 1))

cond = sys.argv[1] if len(sys.argv) > 1 else "pearson"
if cond == "poisson": # option 0: use PoissonCurve rather than Curve to fit
    pass
elif cond == "expected": # option 1: L = (y+1) +/- sqrt(y+1)
    y += 1
    dy = np.sqrt(y)
elif cond == "pearson": # option 2: L = (y + 0.5)  +/- sqrt(y + 1/4)
    dy = np.sqrt(y+0.25)
    y = y + 0.5
elif cond == "expected_mle": # option 3: L = y +/- sqrt(y+1)
    dy = np.sqrt(y+1)
elif cond == "pearson_zero": # option 4: L = y +/- sqrt(y); L[0] = 0.5 +/- 0.5
    dy = np.sqrt(y)
    y = np.asarray(y, 'd')
    y[y == 0] = 0.5
    dy[y == 0] = 0.5
elif cond=="expected_zero": # option 5: L = y +/- sqrt(y);  L[0] = 0 +/- 1
    dy = np.sqrt(y)
    dy[y == 0] = 1.0
else:
    raise RuntimeError("Need to select uncertainty: pearson, pearson_zero, expected, expected_zero, expected_mle, poisson")

if cond == "poisson":
    M = PoissonCurve(peak, x, y, scale=1, center=2, width=2, background=0)
else:
    M = Curve(peak, x, y, dy, scale=1, center=2, width=2, background=0)
dx = max(x)-min(x)
M.scale.range(0, max(y)*1.5)
M.center.range(min(x)-0.2*dx, max(x)+0.2*dx)
M.width.range(0, 0.7*dx)
M.background.range(0, max(y))

problem = FitProblem(M)

