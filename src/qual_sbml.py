import libsbml
import networkx as nx
import numexpr as ne
from itertools import product
from typing import TypedDict
from collections import defaultdict
import src.utils as utils


class FunctionTerm(TypedDict):
    result_level: 0
    math: str


class Transition(TypedDict):
    inputs: list[str]
    outputs: list[str]
    table: dict[tuple, tuple]


def to_hashable(d):
    if isinstance(d, tuple):
        return d
    return tuple(v for _, v in sorted(d.items()))


class QualModel:
    def __init__(self, filename: str):
        sbml: libsbml.SBMLDocument = libsbml.readSBML(filename)

        if sbml.getNumErrors() > 0:
            print(sbml.getErrorLog().toString())
            raise Exception("Error reading SBML file.")

        model: libsbml.QualModelPlugin = sbml.getModel().getPlugin("qual")
        if model is None:
            raise Exception("Model does not contain qualitative information.")

        self.model = model
        self.species = [s.getId() for s in self.model.getListOfQualitativeSpecies()]
        self.transitions, self.max_levels = self._parse_transitions()

    def _parse_transitions(self):
        transitions = []
        max_levels = defaultdict(int)
        for i in range(self.model.getNumTransitions()):
            transition: libsbml.Transition = self.model.getTransition(i)
            inputs = [
                {
                    "id": s.id,
                    "species": s.qualitative_species,
                    "threshold": s.threshold_level,
                }
                for s in transition.getListOfInputs()
            ]
            outputs = [s.qualitative_species for s in transition.getListOfOutputs()]
            default_level = transition.getDefaultTerm().result_level

            max_level = default_level
            function_terms = []
            for func in transition.getListOfFunctionTerms():
                formula = libsbml.formulaToL3String(func.getMath())
                for inp in inputs:
                    if inp["id"]:
                        formula = formula.replace(inp["id"], str(inp["threshold"]))

                formula = formula.replace("&&", "&").replace("||", "|")

                result = func.getResultLevel()
                if result > max_level:
                    max_level = result
                function_terms.append(
                    {
                        "result_level": result,
                        "math": formula,
                    }
                )

            for s in outputs:
                max_levels[s] = max(max_levels[s], max_level)

            transitions.append(
                {
                    "inputs": list({i["species"] for i in inputs}),
                    "outputs": outputs,
                    "default_level": default_level,
                    "function_terms": function_terms,
                }
            )

        return transitions, max_levels

    def _all_states(self):
        ranges = [range(self.max_levels[s] + 1) for s in self.species]
        for state in product(*ranges):
            yield dict(zip(self.species, state))

    def find_attractors(self):
        visited = set()
        steady_states = set()
        cyclic_attractors = set()

        def find_cycle(state):
            cycle = []
            while to_hashable(state) not in cycle:
                cycle.append(to_hashable(state))
                state = self.step(state)

            start = cycle.index(to_hashable(state))
            return cycle[start:]

        for state in self._all_states():
            hashable = to_hashable(state)
            if hashable in visited:
                continue
            cycle = find_cycle(state)
            visited.update(hashable)
            if len(cycle) == 1:
                steady_states.add(cycle[0])
            else:
                cyclic_attractors.add(tuple(sorted(tuple(cycle))))

        return {
            "steady_states": [dict(zip(self.species, s)) for s in steady_states],
            "cyclic_attractors": [
                tuple(dict(zip(self.species, s)) for s in c) for c in cyclic_attractors
            ],
        }

    def plot_state_transitions(self, ax=None):
        attractors = self.find_attractors()

        def node_name(state):
            return "".join(f"{state[s]}" for s in self.species)

        edges = [(node_name(s), node_name(self.step(s))) for s in self._all_states()]

        G = nx.DiGraph()
        G.add_edges_from(edges)

        utils.plot_state_transitions(G, attractors, node_name, ax)

    def plot_interaction_graph(self, ax=None):
        G = nx.MultiDiGraph()
        for t in self.transitions:
            for term in t["function_terms"]:
                for i in t["inputs"]:
                    if i in term["math"]:
                        edges = [(i, o) for o in t["outputs"]]
                        G.add_edges_from(edges)

        utils.plot_interaction_graph(G, ax)

    def step(self, state: dict[str, int] | tuple[int, ...]) -> dict[str, int]:
        if isinstance(state, tuple):
            state = dict(zip(self.species, state))

        next_state = {}
        for t in self.transitions:
            inputs = [state[i] for i in t["inputs"]]
            for f in t["function_terms"]:
                if ne.evaluate(f["math"], local_dict=dict(zip(t["inputs"], inputs))):
                    for s in t["outputs"]:
                        next_state[s] = f["result_level"]
                    break
            else:
                for s in t["outputs"]:
                    next_state[s] = t["default_level"]

        for s in self.species:
            if s not in next_state:
                next_state[s] = 0

        return next_state

    def simulate(
        self, initial_state: dict[str, int], steps: int
    ) -> list[dict[str, int]]:
        trajectory = [initial_state]
        for _ in range(steps):
            next_state = self.step(trajectory[-1])
            trajectory.append(next_state)
        return trajectory
