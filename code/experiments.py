# a real pipeline
import sys as sys
import validator as val
import injector as inj
from onto_graph import OntoGraph

path_data = "../data/"
source_path = path_data + "000/onto.owl"  # fixed source path 000/onto.owl

"""
Run experiments through all steps
    (1) inject a fraction of wrong sameAs links in
    (2) validate the erroneous files --> result: #wrong sameAs found/#sameAs added
    (3) compute the avg over all 80 input folders
    
Required parameters:
    - threshold:    to compute the degree functionality of a property
    - ratio:        fraction of manually added erroneous sameAs (as an integer)
    - do_injection: to include wrong sameAs injection to the experiments
                    (False if we've already done it, to prevent redundant work & loss of time)
"""

# prompt for custom parameters, if not provided, take default values
if len(sys.argv) < 5:
    print("Syntax: python experiments.py num_input(from 1 to 80) threshold(float) ratio(float) do_injection(boolean)")
    sys.exit(0)
else:
    # otherwise, parse from the command line
    num_input = int(sys.argv[1])
    threshold = float(sys.argv[2])
    ratio = float(sys.argv[3])
    do_inj = bool(sys.argv[4])

# inject erroneous sameAs in all input folder
if do_inj:
    print("Injecting erroneous sameAs links...")
    for i in range(1, num_input+1):
        folder = "00" + str(i) + "/" if i < 10 else "0" + str(i) + "/"
        target_path = path_data + folder + "onto.owl"
        refalign_path = path_data + folder + "refalign.rdf"
        output_path = path_data + folder + "err_refalign.rdf"

        # create the graphs, no need to extract functional properties
        g_source = OntoGraph(source_path)
        g_target = OntoGraph(target_path)

        inj.create_wrong_sameas(target_graph=g_target, source_graph=g_source,
                                output_path=output_path, target_refalign_path=refalign_path,
                                ratio=ratio)
        print("\tDone injecting in " + folder)

# create the source ontology 000/onto.owl
g_source = OntoGraph(path_data + source_path)
g_source.extract_func_properties(threshold=threshold)

# run validation for each input folder
for i in range(1, num_input+1):
    # get the folder name
    folder = "00" + str(i) + "/" if i < 10 else "0" + str(i) + "/"

    # the target graph (anything of 00i/onto.owl where i != 0)
    target_path = path_data + folder + "onto.owl"
    g_target = OntoGraph(path_data + target_path)
    g_target.extract_func_properties(threshold=threshold)

    # the set of sameAs links to validate
    val_path = path_data + folder + "err_refalign.rdf"
    to_validate = inj.extract_sameas(path_data + val_path)
    V = inj.count_links(val_path)

    # we also want to keep track of the number of wrong sameAs being added in
    gold_path = path_data + folder + "refalign.rdf"
    G = inj.count_links(path_data + gold_path)
    print("Golden standard:", G)
    print("To validate:", V)
    print("Ratio:", ratio)
    assert int(G / V) == int(1 / (1 + ratio))

    # validate sameAs statements
    num_true, num_false = val.detect_false_sameas(to_validate, g_source, g_target)
    print("%d wrong sameAs links detected over %d erroneous links" % (num_false, V-G))
