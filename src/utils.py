import matplotlib.pyplot as plt
from typing import List, Dict


def plot_trajectory(
    trajectory: List[Dict[str, bool]],
    species_names: List[str],
    title: str = "Boolean Network Simulation",
):
    plt.figure(figsize=(10, 5))
    times = range(len(trajectory))
    for species in species_names:
        values = [int(state[species]) for state in trajectory]
        plt.step(times, values, label=species, where="post")

    plt.title(title)
    plt.xlabel("Time steps")
    plt.ylabel("State (0/1)")
    plt.grid(True)
    plt.legend()
    plt.show()


def print_boolean_rules(bool_solver):
    print("Boolean rules:")
    for species, rule in bool_solver.get_boolean_rules().items():
        print(f"{species} = {rule}")


def print_attractors(attractors):
    print("\nAttractors found:")
    print("Steady states:", attractors["steady_states"])
    print("Cyclic attractors:", attractors["cyclic_attractors"])
