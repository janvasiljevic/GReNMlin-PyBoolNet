from src.bool_sim import BooleanSolver
from src.grn import GRN
from src.utils import plot_trajectory, print_boolean_rules, print_attractors


def create_network():
    """Create a GRN implementing a toggle switch."""
    grn = GRN()

    grn.add_species("X", 0.1)
    grn.add_species("Y", 0.1)

    regulators1 = [{"name": "Y", "type": -1, "Kd": 1, "n": 2}]
    products1 = [{"name": "X"}]
    grn.add_gene(1, regulators1, products1)

    regulators2 = [{"name": "X", "type": -1, "Kd": 1, "n": 2}]
    products2 = [{"name": "Y"}]
    grn.add_gene(1, regulators2, products2)

    return grn


def main():
    grn = create_network()
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
