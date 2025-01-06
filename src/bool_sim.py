import numpy as np
from typing import Dict, List, Literal
import pyboolnet.attractors
import pyboolnet.file_exchange
import pyboolnet.state_transition_graphs
import src.grn as grn
from typing import TypedDict


class Attractors(TypedDict):
    steady_states: List[Dict[str, bool]]
    cyclic_attractors: List[List[Dict[str, bool]]]


SimulationType = Literal["async", "sync"]


class BooleanSolver:
    def __init__(self, grn: grn.GRN):
        """
        Initialize Boolean solver for a GRN
        """
        self.grn = grn
        # X: var_X -> We need this, because external ASP solver requires length >= 2
        self.original_names = {
            name: f"var_{name}" if len(name) < 2 else name for name in grn.species_names
        }
        # simple LUT
        self.reverse_names = {v: k for k, v in self.original_names.items()}
        self.boolean_rules = self._generate_boolean_rules()

        print("Boolean rules:", self.boolean_rules)

    def _generate_boolean_rules(self) -> Dict[str, str]:
        """
        Convert GRN structure to Boolean rules with renamed variables

        Returns:
            Dictionary mapping species names to their Boolean update rules:
            {species_name: "expression"} where expression is a Boolean expression.
            {'X1': 'X1', 'X2': 'X2', 'var_Y': '((X2) & (!X1)) | ((X1) & (!X2))'}
        """
        rules = {}

        for species in self.grn.species_names:
            rules[self.original_names[species]] = []

        for gene in self.grn.genes:
            products = [self.original_names[p["name"]] for p in gene["products"]]
            activators = []
            inhibitors = []

            # separate activators and inhibitors
            for reg in gene["regulators"]:
                reg_name = self.original_names[reg["name"]]
                if reg["type"] == 1:
                    activators.append(reg_name)
                else:
                    inhibitors.append(reg_name)

            # possible: 'and', 'or', ''
            if gene["logic_type"] == "and":
                act_expr = " & ".join(activators) if activators else "1"
                inh_expr = (
                    " & ".join([f"!{inh}" for inh in inhibitors]) if inhibitors else "1"
                )
                expr = f"({act_expr}) & ({inh_expr})"
            elif gene["logic_type"] == "or":
                terms = []
                if activators:
                    terms.append(" | ".join(activators))
                terms.extend([f"!{inh}" for inh in inhibitors])
                expr = f'({" | ".join(terms)})'

            for product in products:
                rules[product].append(expr)

        # combine rules
        final_rules = {}
        for species, expressions in rules.items():
            if expressions:
                final_rules[species] = " | ".join([f"({expr})" for expr in expressions])
            else:
                # input species or no regulators
                final_rules[species] = species

        return final_rules

    def _rules_to_bnet_text(self) -> str:
        """Convert boolean rules dictionary to BNet format text"""
        bnet_lines = []
        for species, rule in self.boolean_rules.items():
            bnet_lines.append("targets, factors")
            bnet_lines.append(f"{species}, {rule}")
        return "\n".join(bnet_lines)

    def get_boolean_rules(self) -> Dict[str, str]:
        """Return the generated Boolean rules with original variable names"""
        original_rules = {}
        for species, rule in self.boolean_rules.items():
            original_name = self.reverse_names[species]
            rule_original = rule
            for old_name, new_name in self.original_names.items():
                rule_original = rule_original.replace(new_name, old_name)
            original_rules[original_name] = rule_original
        return original_rules

    def simulate(
        self,
        initial_state: Dict[str, bool],
        mode: SimulationType = "async",
        steps: int = 100,
    ) -> List[Dict[str, bool]]:
        """
        Simulate asynchronous Boolean network dynamics

        Args:
            initial_state: Dictionary mapping species names to initial Boolean values
            steps: Number of simulation steps

        Returns:
            List of states (dictionaries) representing the trajectory
        """
        assert mode in ["async", "sync"], "Invalid simulation type"

        # Convert initial state to use renamed variables
        renamed_initial_state = {
            self.original_names[k]: v for k, v in initial_state.items()
        }

        # Convert rules to BNet format text
        bnet_text = self._rules_to_bnet_text()

        # Convert to PyBoolNet primes
        primes = pyboolnet.file_exchange.bnet_text2primes(bnet_text)

        # Initialize trajectory
        trajectory = []
        current_state = renamed_initial_state.copy()

        # Add initial state with original names
        trajectory.append({self.reverse_names[k]: v for k, v in current_state.items()})

        for _ in range(steps):
            # Get possible successor states

            if mode == "sync":
                successors = pyboolnet.state_transition_graphs.successor_synchronous(
                    primes, current_state
                )
            else:
                successors = pyboolnet.state_transition_graphs.successors_asynchronous(
                    primes, current_state
                )

            if not successors:
                break

            if mode == "sync":
                next_state = successors

            else:
                successor_dicts = []
                for state in successors:
                    successor_dicts.append(state)

                if not successor_dicts:
                    break

                # Most basic asynchronous update: randomly choose one of the possible states
                next_state = successor_dicts[np.random.randint(len(successor_dicts))]

            # Convert state back to original names for trajectory
            trajectory.append({self.reverse_names[k]: v for k, v in next_state.items()})
            current_state = next_state.copy()

        return trajectory

    def find_attractors(self) -> Attractors:
        """
        Find all attractors in the Boolean network using Tarjan's algorithm
        """
        bnet_text = self._rules_to_bnet_text()
        primes = pyboolnet.file_exchange.bnet_text2primes(bnet_text)

        # state transition graph
        stg = pyboolnet.state_transition_graphs.primes2stg(primes, "asynchronous")

        # if using just compute_attractors, you need ASP solvers like clingo
        steady_states, cyclic_attractors = (
            pyboolnet.attractors.compute_attractors_tarjan(stg)
        )

        def state_str_to_dict(state_str: str) -> Dict[str, bool]:
            """
            Convert from "101" to {"X1": True, "X2": False, "Y": True}
            """
            state_dict = {}
            for _, (var_name, val) in enumerate(
                zip(self.boolean_rules.keys(), state_str)
            ):
                state_dict[self.reverse_names[var_name]] = val == "1"
            return state_dict

        result: Attractors = {"steady_states": [], "cyclic_attractors": []}

        for state in steady_states:
            result["steady_states"].append(state_str_to_dict(state))

        # Process cyclic attractors
        for attractor_states in cyclic_attractors:
            cyclic_attractor = []
            for state in attractor_states:
                cyclic_attractor.append(state_str_to_dict(state))
            result["cyclic_attractors"].append(cyclic_attractor)

        return result
