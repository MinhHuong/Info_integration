""" pipeline.py: Runs the validator on a file containing correct and incorrect same-as links

This file is for test purpose only.
"""

import sys as sys
import validator as val
from onto_graph import OntoGraph
import injector as inj

__authors__ = "Billel Guerfa, Armita Khajehnassiri, Minh-Huong Le-Nguyen, Nafaa Si Said"


# prompt for custom parameters, if not provided, take default values
# syntax: 'python pipeline.py <source_graph> <target_graph> <to_validate> <threshold> <depth>'
if len(sys.argv) < 6:
    print("Syntax: python pipeline.py <source_graph> <target_graph> <to_validate> <threshold> <depth>")
    sys.exit(0)

# otherwise, parse from the command line
print("Extracting custom parameters...")
source_path = sys.argv[1]
target_path = sys.argv[2]
val_path = sys.argv[3]
threshold = float(sys.argv[4])
depth = int(sys.argv[5])

print("Extracting functional propreties...")

# the source graph (must always be 000/onto.owl)
g_source = OntoGraph(source_path)
g_source.extract_func_properties(threshold=threshold)

# the target graph (anything of 00i/onto.owl where i != 0)
g_target = OntoGraph(target_path)
g_target.extract_func_properties(threshold=threshold)

# the set of sameAs links to validate
to_validate = inj.extract_sameas(val_path)

# validate sameAs statements
print("Detecting false sameAs statements...")
wrong_sameas = val.invalidate_sameas(to_validate, g_source, g_target, depth)
print("Number of wrong same-as:", len(wrong_sameas))
