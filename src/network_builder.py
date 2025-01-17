from __future__ import annotations
from src.grn import GRN


class Species:
    def __init__(self, name, delta=None):
        self.name = name

    def activates(self, Kd=1, n=1):
        return {"name": self.name, "type": 1, "Kd": Kd, "n": n}

    def represses(self, Kd=1, n=1):
        return {"name": self.name, "type": -1, "Kd": Kd, "n": n}


class Builder:
    def __init__(self):
        self.grn = GRN()

    def species(self, name, delta=None) -> Species:
        if delta:
            self.grn.add_species(name, delta)
        else:
            self.grn.add_input_species(name)
        return Species(name, delta)

    def gene(self, regulators: list[dict], products: list[Species], alpha: float = 1):
        self.grn.add_gene(
            alpha, regulators, [{"name": product.name} for product in products]
        )
