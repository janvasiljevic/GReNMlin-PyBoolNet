import numpy as np
import src.simulator as simulator
from src.helpers import powerset
from typing import Dict, List, TypedDict, Literal

import networkx as nx
import matplotlib.pyplot as plt


LogicType = Literal["and", "or", ""]


class Species(TypedDict):
    name: str
    delta: float


class Regulator(TypedDict):
    name: str
    type: Literal[-1, 1]
    Kd: float
    n: float


class Product(TypedDict):
    name: str


class Gene(TypedDict):
    alpha: float
    regulators: List[Regulator]
    products: List[Product]
    logic_type: LogicType


class GRN:
    def __init__(self):
        self.species: List[Species] = []
        self.species_names: List[str] = []
        self.input_species_names: List[str] = []
        self.genes: List[Gene] = []

    def add_input_species(self, name: str):
        """
        Adds an input species to the GRN.
        Input species do not degrade.
        """
        self.add_species(name, 0)
        self.input_species_names.append(name)

    def add_species(self, name: str, delta: float):
        self.species.append({"name": name, "delta": delta})
        self.species_names.append(name)

    """
        regulator = {'name': str - name,
                     'type': int - -1 / 1],
                     'Kd': Kd,
                     'n': n}
        product = {'name': str - name}

    """

    def add_gene(
        self,
        alpha: float,
        regulators: List[Regulator],
        products: List[Product],
        input_logic_type: Literal[LogicType, "mixed"] = "and",
    ) -> None:
        """
        Adds a gene to the GRN.

        Parameters:
        alpha: production rate of the gene
        regulators: list of regulators
        products: list of products
        input_logic_type: type of logic to be used for the gene (and/or/mixed/'')
        """

        assert input_logic_type in ["and", "or", "mixed", ""], "Invalid logic type"

        logic_type: LogicType = input_logic_type

        if input_logic_type == "mixed":
            logic_type = np.random.choice(["and", "or"])

        gene = {
            "alpha": alpha,
            "regulators": regulators,
            "products": products,
            "logic_type": logic_type,
        }

        for regulator in regulators:
            if regulator["name"] not in self.species_names:
                print(f'{regulator["name"]} not in species!')

        for product in products:
            if product["name"] not in self.species_names:
                print(f'{product["name"]} not in species!')

        self.genes.append(gene)

    def generate_equations(self) -> Dict[str, List[str]]:
        """
        Generate system of equations describing the network dynamics.
        """
        equations: Dict[str, List[str]] = {}

        for species in self.species:
            equations[species["name"]] = [f'-{species["name"]}*{species["delta"]}']

        for gene in self.genes:
            up: List[str] = []
            down: List[str] = []
            logic_type = gene["logic_type"]

            for regulator in gene["regulators"]:
                name = regulator["name"]
                n = regulator["n"]
                Kd = regulator["Kd"]

                regulator_term = f"(({name}/{Kd})**{n})"

                if regulator["type"] == 1:
                    up.append(regulator_term)

                down.append(regulator_term)

            if not up:
                up = ["1"]

            if logic_type == "or":
                up = "+".join(powerset(up, op="*"))
            elif logic_type == "and":
                up = "*".join(up)
            elif logic_type == "":
                up = up[0]
            else:
                raise ValueError("Invalid logic type. Must be 'and', 'or' or ''")

            down = "+".join(["1"] + powerset(down, op="*"))

            terms = f'{gene["alpha"]}*({up})/({down})'

            for product in gene["products"]:
                equations[product["name"]].append(terms)

        return equations

    def generate_model(self, fname: str = "model.py") -> None:
        """
        Generate a Python module containing the model equations.
        """
        equations = self.generate_equations()

        with open(fname, "w") as f:
            print("import numpy as np \n", file=f)
            print("def solve_model(T,state):", file=f)

            all_keys = ", ".join(equations.keys())
            all_dkeys = ", ".join([f"d{key}" for key in equations.keys()])

            print(f"    {all_keys} = state", file=f)

            for key in equations.keys():
                print(f'    d{key} = {"+".join(equations[key])}', file=f)

            print(f"    return np.array([{all_dkeys}])", file=f)

            print("", file=f)
            print("def solve_model_steady(state):", file=f)
            print("    return solve_model(0, state)", file=f)

    def plot_network(self) -> None:
        """
        Visualize the network structure.
        """
        activators: Dict[str, List[str]] = {s: [] for s in self.species_names}
        inhibitors: Dict[str, List[str]] = {s: [] for s in self.species_names}

        for gene in self.genes:
            for product in gene["products"]:
                activators[product["name"]].extend(
                    [x["name"] for x in gene["regulators"] if x["type"] == 1]
                )
                inhibitors[product["name"]].extend(
                    [x["name"] for x in gene["regulators"] if x["type"] == -1]
                )

        edges_act = set()
        edges_inh = set()

        for prod in activators:
            for reg in activators[prod]:
                edges_act.add((reg, prod))

        for prod in inhibitors:
            for reg in inhibitors[prod]:
                edges_inh.add((reg, prod))

        edges_both = edges_act & edges_inh
        edges_act -= edges_both
        edges_inh -= edges_both

        edges = list(edges_both) + list(edges_act) + list(edges_inh)

        G = nx.DiGraph()
        G.add_edges_from(edges)

        edges = list(G.edges)
        colors = []
        for edge in edges:
            if edge in edges_both:
                colors.append("orange")
            elif edge in edges_act:
                colors.append("blue")
            elif edge in edges_inh:
                colors.append("red")

        nx.draw_networkx(
            G, pos=nx.circular_layout(G), arrows=True, node_color="w", edge_color=colors
        )
        plt.show()


if __name__ == "__main__":
    my_grn = GRN()
    my_grn.add_input_species("X1")
    my_grn.add_input_species("X2")

    my_grn.add_species("Y", 0.1)

    # print(my_grn.species)
    # print(my_grn.species_names)

    regulators = [
        {"name": "X1", "type": -1, "Kd": 5, "n": 2},
        {"name": "X2", "type": 1, "Kd": 5, "n": 3},
    ]
    products = [{"name": "Y"}]
    my_grn.add_gene(10, regulators, products)

    regulators = [
        {"name": "X1", "type": 1, "Kd": 5, "n": 2},
        {"name": "X2", "type": -1, "Kd": 5, "n": 3},
    ]
    products = [{"name": "Y"}]
    my_grn.add_gene(10, regulators, products)

    # print(my_grn.genes)

    IN = np.zeros(len(my_grn.input_species_names))
    IN[0] = 100
    IN[1] = 100

    simulator.simulate_single(my_grn, IN)
