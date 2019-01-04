# a real pipeline
import sys as sys
import validator as val
from onto_graph import OntoGraph
import injector as inj

path_data = "../data/"

# N.B.: the injection is done separately
# the main pipeline does not concern with manual injection of erroneous links

# prompt for custom parameters, if not provided, take default values
# syntax: 'python pipeline.py <source_graph> <target_graph> <to_validate> <threshold>'
if len(sys.argv) < 5:
    print("Default values will be used.")
    source_path = path_data + "000/onto.owl"
    target_path = path_data + "001/onto.owl"
    val_path = path_data + "001/err_refalign.rdf"
    threshold = 0.8
else:
    # otherwise, parse from the command line
    print("Extracting custom parameters...")
    source_path = sys.argv[1]
    target_path = sys.argv[2]
    val_path = sys.argv[3]
    threshold = float(sys.argv[4])

# the source graph (must always be 000/onto.owl)
g_source = OntoGraph(path_data + source_path)
g_source.extract_func_properties(threshold=threshold)

# the target graph (anything of 00i/onto.owl where i != 0)
g_target = OntoGraph(path_data + target_path)
g_target.extract_func_properties(threshold=threshold)

# the set of sameAs links to validate
to_validate = inj.extract_sameas(path_data + val_path)

# validate sameAs statements
val.detect_false_sameas(to_validate, g_source, g_target)
