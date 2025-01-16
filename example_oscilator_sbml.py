from src import simulator
from src.grn import GRN
from src.qual_sbml import QualModel


def main():
    qual_model = QualModel("qualSBML/regulator.xml")
    attr = qual_model.find_attractors()
    print(attr)
    qual_model.plot_network()


if __name__ == "__main__":
    main()
