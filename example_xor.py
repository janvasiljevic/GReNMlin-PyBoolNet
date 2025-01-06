from src.bool_sim import BooleanSolver
from src.grn import GRN
from src.utils import plot_trajectory, print_boolean_rules, print_attractors


def create_network():
    """Create a GRN implementing XOR logic."""
    grn = GRN()

    grn.add_input_species("X1")
    grn.add_input_species("X2")
    grn.add_species("Y", 0.1)

    regulators1 = [
        {"name": "X1", "type": -1, "Kd": 5, "n": 2},
        {"name": "X2", "type": 1, "Kd": 5, "n": 3},
    ]
    products1 = [{"name": "Y"}]
    grn.add_gene(10, regulators1, products1)

    regulators2 = [
        {"name": "X1", "type": 1, "Kd": 5, "n": 2},
        {"name": "X2", "type": -1, "Kd": 5, "n": 3},
    ]
    products2 = [{"name": "Y"}]
    grn.add_gene(10, regulators2, products2)

    return grn


def main():
    grn = create_network()
    bool_solver = BooleanSolver(grn)

    print_boolean_rules(bool_solver)

    initial_state = {"X1": True, "X2": False, "Y": False}
    trajectory = bool_solver.simulate(initial_state, "sync", steps=20)

    plot_trajectory(trajectory, grn.species_names, "XOR Network Simulation")

    attractors = bool_solver.find_attractors()
    print_attractors(attractors)


if __name__ == "__main__":
    main()
