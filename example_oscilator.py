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

    grn.gene([Z.represses(Kd=1, n=2)], [X])
    grn.gene([X.represses(Kd=1, n=2)], [Y])
    grn.gene([Y.represses(Kd=1, n=2)], [Z])

    grn = grn.grn

    grn.plot_network()

    bool_solver = BooleanSolver(grn)

    print_boolean_rules(bool_solver)

    initial_state = {"X": True, "Y": False, "Z": False}
    trajectory = bool_solver.simulate(initial_state, "async")

    plot_trajectory(trajectory, grn.species_names, "Repressilator Simulation")

    attractors = bool_solver.find_attractors()
    print_attractors(attractors)


if __name__ == "__main__":
    main()
