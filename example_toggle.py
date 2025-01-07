from src.bool_sim import BooleanSolver
from src.network_builder import Builder
from src.utils import plot_trajectory, print_boolean_rules, print_attractors

def main():
    grn = Builder()
    X = grn.species("X", 0.1)
    Y = grn.species("Y", 0.1)

    grn.gene([Y.represses(Kd=1, n=2)], [X])
    grn.gene([X.represses(Kd=1, n=2)], [Y])
    grn = grn.grn
    bool_solver = BooleanSolver(grn)

    grn.plot_network()

    print_boolean_rules(bool_solver)

    initial_states = [
        {"X": True, "Y": False},
        {"X": False, "Y": True},
        {"X": True, "Y": True},
    ]

    for i, initial_state in enumerate(initial_states):
        trajectory = bool_solver.simulate(initial_state, steps=20)
        plot_trajectory(
            trajectory, grn.species_names, f"Toggle Switch Simulation {i+1}"
        )

    attractors = bool_solver.find_attractors()
    print_attractors(attractors)


if __name__ == "__main__":
    main()
