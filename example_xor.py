from src.bool_sim import BooleanSolver
from src.network_builder import Builder
from src.utils import plot_trajectory, print_boolean_rules, print_attractors

def main():
    grn = Builder()
    X1 = grn.species("X1")
    X2 = grn.species("X2")
    Y = grn.species("Y", 0.1)

    grn.gene([X1.represses(Kd=5, n=2), X2.activates(Kd=5, n=3)], [Y], 10)
    grn.gene([X1.activates(Kd=5, n=2), X2.represses(Kd=5, n=3)], [Y], 10)
    grn = grn.grn
    grn.plot_network()
    bool_solver = BooleanSolver(grn)

    print_boolean_rules(bool_solver)

    initial_state = {"X1": True, "X2": False, "Y": False}
    trajectory = bool_solver.simulate(initial_state, "sync", steps=20)

    plot_trajectory(trajectory, grn.species_names, "XOR Network Simulation")

    attractors = bool_solver.find_attractors()
    print_attractors(attractors)


if __name__ == "__main__":
    main()
