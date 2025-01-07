import numpy as np
from src import simulator
from src.bool_sim import BooleanSolver
from src.network_builder import Builder
from src.utils import plot_trajectory, print_boolean_rules, print_attractors

def main():
    grn = Builder()

    X = grn.species("X", 0.1)
    Y = grn.species("Y", 0.1)
    Z = grn.species("Z", 0.1)

    grn.gene([Z.represses(Kd=1, n=5)], [X])
    grn.gene([X.represses(Kd=1, n=5)], [Y])
    grn.gene([Y.represses(Kd=1, n=5)], [Z])

    grn = grn.grn
    grn.plot_network()

    T, Y = simulator.simulate_single(grn, [], t_end=1000)


if __name__ == "__main__":
    main()
