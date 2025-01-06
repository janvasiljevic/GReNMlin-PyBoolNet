import numpy as np 

def solve_model(T,state):
    X, Y, Z = state
    dX = -X*0.1+1*(1)/(1+((Z/1)**5))
    dY = -Y*0.1+1*(1)/(1+((X/1)**5))
    dZ = -Z*0.1+1*(1)/(1+((Y/1)**5))
    return np.array([dX, dY, dZ])

def solve_model_steady(state):
    return solve_model(0, state)
