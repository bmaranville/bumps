import numpy as np
from math import log
from scipy.stats import distributions, multivariate_normal
from bumps.names import *
from bumps.dream.entropy import Box, MultivariateT, Joint

USAGE = """
Usage: bumps check_entropy.py dist p1 p2 ...

where dist is one of the distributions in scipy.stats.distributions and
p1, p2, ... are the arguments for the distribution in the order that they
appear. For example, for the normal distribution, x ~ N(3, 0.8), use:

    bumps --fit=dream --entropy  --store=/tmp/T1 check_entropy.py norm 3 0.2
"""
def _mu_sigma(mu, sigma):
    sigma = np.asarray(sigma)
    if len(sigma.shape) == 1:
        sigma = np.diag(sigma**2)
    if mu is None:
        mu = np.zeros(sigma.shape[0])
    return mu, sigma

def mvn(sigma, mu=None):
    mu, sigma = _mu_sigma(mu, sigma)
    return multivariate_normal(mean=mu, cov=sigma)

def mvskewn(alpha, sigma, mu=None):
    sigma = np.asarray(sigma)
    assert len(sigma.shape) == 1
    if mu is None:
        mu = np.zeros(sigma.shape[0])
    Dk = [distributions.skewnorm(alpha, m, s) for m, s in zip(mu, sigma)]
    return Joint(Dk)

def mvt(df, sigma, mu=None):
    mu, sigma = _mu_sigma(mu, sigma)
    return MultivariateT(mu=mu, sigma=sigma, df=df)

def mvcauchy(sigma, mu=None):
    mu, sigma = _mu_sigma(mu, sigma)
    return MultivariateT(mu=mu, sigma=sigma, df=1)

DISTS = {
    'mvn': mvn,
    'mvt': mvt,
    'mvskewn': mvskewn,
    'mvcauchy': mvcauchy,
    'mvu': Box,
}
if len(sys.argv) > 1:
    dist_name = sys.argv[1]
    D_class = DISTS.get(dist_name, None)
    if D_class is None:
        D_class = getattr(distributions, dist_name, None)
    if D_class is None:
        print("unknown distribution " + dist_name)
        sys.exit()
    args = [[[float(vjk) for vjk in vj.split(',')] for vj in v.split(',')] if ';' in v
            else [float(vj) for vj in v.split(',')] if ',' in v
            else float(v)
            for v in sys.argv[2:]]
    D = D_class(*args)
else:
    print(USAGE)
    sys.exit()

def D_nllf(x):
    return -D.logpdf(x)
dim = getattr(D, 'dim', 1)
if dim == 1:
    M = PDF(D_nllf, x=0.9)
    M.x.range(-inf, inf)
else:
    M = VectorPDF(D_nllf, np.ones(dim))
    for k in range(dim):
        getattr(M, 'p'+str(k)).range(-inf, inf)

if dist_name == "mvskewn":
    for k in range(dim):
        getattr(M, 'p'+str(k)).value = D.distributions[k].mean()

problem = FitProblem(M)

entropy = D.entropy()
print("*** Expected entropy: %.4f bits %.4f nats"%(entropy/log(2), entropy))

