import numpy as np
from src import simulator
from src.bool_sim import BooleanSolver
from src.grn import GRN
from src.utils import plot_trajectory, print_boolean_rules, print_attractors


def create_network():
    """Create a repressilator with an input signal that can trigger X."""
    grn = GRN()

    # Add core oscillator species
    grn.add_species("X", 0.1)
    grn.add_species("Y", 0.1)
    grn.add_species("Z", 0.1)

    regulators1 = [{"name": "Z", "type": -1, "Kd": 1, "n": 5}]
    products1 = [{"name": "X"}]
    grn.add_gene(1, regulators1, products1)

    regulators2 = [{"name": "X", "type": -1, "Kd": 1, "n": 5}]
    products2 = [{"name": "Y"}]
    grn.add_gene(1, regulators2, products2)

    regulators3 = [{"name": "Y", "type": -1, "Kd": 1, "n": 5}]
    products3 = [{"name": "Z"}]
    grn.add_gene(1, regulators3, products3)

    return grn


def main():
    grn = create_network()

    grn.plot_network()

    T, Y = simulator.simulate_single(grn, [], t_end=1000)


if __name__ == "__main__":
    main()
