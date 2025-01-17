import matplotlib.pyplot as plt
from typing import List, Dict
import networkx as nx
import numpy as np


def plot_trajectory(
    trajectory: List[Dict[str, bool]],
    species_names: List[str],
    title: str = "Boolean Network Simulation",
    ax=None,
    ymin=None,
    ymax=None,
):
    if ax is None:
        ax = plt.gca()

    times = np.arange(len(trajectory)) - 0.5
    for species in species_names:
        values = [int(state[species]) for state in trajectory]
        ax.step(times, values, label=species, where="post", alpha=0.7)

    ax.set_title(title)
    ax.set_xlabel("Time steps")
    ax.set_xticks(range(len(trajectory)))
    ax.set_ylabel("State")
    ax.set_ylim(ymin=ymin, ymax=ymax)
    # ax.grid(True)
    ax.legend()


def print_boolean_rules(bool_solver):
    print("Boolean rules:")
    for species, rule in bool_solver.get_boolean_rules().items():
        print(f"{species} = {rule}")


def print_attractors(attractors):
    print("\nAttractors found:")
    print("Steady states:", attractors["steady_states"])
    print("Cyclic attractors:", attractors["cyclic_attractors"])


def plot_state_transitions(G: nx.DiGraph, attractors, name_func=lambda x: x, ax=None):
    node_colors = {n: "lightblue" for n in G.nodes}
    for attr in attractors["steady_states"]:
        node_colors[name_func(attr)] = "green"

    for attrs in attractors["cyclic_attractors"]:
        for a in attrs:
            node_colors[name_func(a)] = "red"

    if ax is None:
        ax = plt.gca()

    ax.set_title("State Transition Graph")
    nx.draw(
        G,
        with_labels=True,
        pos=nx.circular_layout(G),
        node_size=1000,
        node_color=[node_colors[n] for n in G.nodes],
        ax=ax,
    )


def plot_interaction_graph(G: nx.DiGraph, ax=None):
    if ax is None:
        ax = plt.gca()

    ax.set_title("Interaction Graph")
    nx.draw(
        G,
        with_labels=True,
        pos=nx.circular_layout(G),
        node_size=1500,
        node_color="lightblue",
        ax=ax,
    )
