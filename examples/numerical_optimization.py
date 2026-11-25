# Example of optimization using
# fmin_cg : nonlinear conjugate gradient algorithm
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_cg.html

import scipy
from scipy.optimize import fmin_cg

# Function to be minimized (wrt. vector z)
def f(z):
        x=z[0];y=z[1];
        return (x-1)**2+(y-3)**2

z0 = [0,0]  # Initial value
res=scipy.optimize.fmin_cg(f, z0) 
print(res)





