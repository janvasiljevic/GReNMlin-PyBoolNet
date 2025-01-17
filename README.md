# Bool-GReNMlin

> This is a fork of the original GRenMlin repository. It aims to add a simulation module using Boolean networks.

Besides installing the needed dependencies, you will also need to install `clasp` and `gringo` from the [Potassco](https://potassco.org/) project.

For MacOS:

```bash
brew install clingo
```

## Other changes

- Project management with `poetry`.
- Type hints.
- Deleted the `params.py` file.
- PyBoolNet integration
- Reading and simulation of qual SBML models

- TODO: Matej/Enei/Lan add

## Possible sources:

- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140954

## Original description

GReNMlin (Gene Regulatory Network Modeling) is a package for constructing and simulating models of gene regulatory networks. Its main modules are:

- [`grn.py`](grn.py): supports building and modifactions of gene regulatory network models.
- [`simulator.py`](simulator.py): supports different types of simulations of models build with [`grn.py`](grn.py).
- [`helpers.py`](helpers.py): helper functions.

Demonstrative examples are provided in [`examples.ipynb`](examples.ipynb).

![GRenMlin](logo.png)
