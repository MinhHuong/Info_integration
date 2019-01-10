# a real pipeline
import sys as sys
import validator as val
import injector as inj
from onto_graph import OntoGraph
import utils as ut
import time as tm


path_data = "../data/"
source_path = path_data + "000/onto.owl"  # fixed source path 000/onto.owl

"""
Run experiments through all steps
    (1) inject a fraction of wrong sameAs links in
    (2) validate the erroneous files --> result: #wrong sameAs found/#sameAs added
    (3) compute the avg over all 80 input folders
    
Required parameters:
    - num_input:    number of input folders to work on (from 1 to 80 inclusively)
    - threshold:    to compute the degree functionality of a property
    - ratio:        fraction of manually added erroneous sameAs (as an integer)
"""

# prompt for custom parameters, if not provided, take default values
if len(sys.argv) < 6:
    print("Syntax: python experiments.py from to threshold(float) ratio(float) depth[0, )")
    print("'from' and 'to' accept value in [1, 80]")
    print("Leave 'to' = -1 if you want to test in one folder only")
    sys.exit(0)
else:
    # otherwise, parse from the command line
    start_input = int(sys.argv[1])
    end = int(sys.argv[2])
    if end != -1 and end < start_input:
        print("'from' folder must be smaller than 'to' folder!")
        sys.exit(0)
    end_input = end if end != -1 else start_input
    threshold = float(sys.argv[3])
    ratio = float(sys.argv[4])
    depth = int(sys.argv[5])

# create the source ontology 000/onto.owl
g_source = OntoGraph(path_data + source_path)
g_source.extract_func_properties(threshold=threshold)

# csv file to store output
fout = open(
    "../experiments/recent/depth/random_result"
    + "_" + str(start_input)
    + "_" + str(end_input)
    + "_" + str(threshold)
    + "_" + str(ratio)
    + "_" + str(depth)
    + ".csv",
    "w")
fout.write("# start_input : " + sys.argv[1] + "\n")
fout.write("# end_input : " + sys.argv[2] + "\n")
fout.write("# threshold : " + sys.argv[3] + "\n")
fout.write("# ratio : " + sys.argv[4] + "\n")
fout.write("# depth :" + sys.argv[5] + "\n")
fout.write("Folder,Precision,Recall,Time(s)" + "\n")

for i in range(start_input, end_input+1):
    # setup the input data
    folder = "00" + str(i) + "/" if i < 10 else "0" + str(i) + "/"
    target_path = path_data + folder + "onto.owl"
    refalign_path = path_data + folder + "refalign.rdf"
    val_path = path_data + folder + "err_refalign.rdf"

    # start the party
    print("Working in folder %s..." % folder)
    start_time = tm.time()

    # create the target graph & extract functional properties
    # print("Extracting functional properites in " + target_path + "\n")
    g_target = OntoGraph(target_path)
    g_target.extract_func_properties(threshold=threshold)

    # inject erroneous sameAs in all input folder then do validation
    # print("Injecting erroneous sameAs links in " + val_path + "\n")
    error_links = inj.create_wrong_sameas(target_graph=g_target, source_graph=g_source,
                            output_path=val_path, target_refalign_path=refalign_path,
                            ratio=ratio)

    # set to validate after injection
    # print("Validating all the sameAs links in " + val_path + "\n")
    val_set = inj.extract_sameas(val_path)
    V = len(val_set)

    # the golden standard i.e. all the correct sameAs
    gold_set = inj.extract_sameas(refalign_path)
    G = len(gold_set)

    # sanity check
    assert int(G / V) == int(1 / (1 + ratio))

    # validate the sameAs links
    wrong_sameas = val.invalidate_sameas(val_set, g_source, g_target, depth)
    inters = ut.find_intersection(wrong_sameas, error_links)
    end_time = tm.time()

    # print("#False sameAs links found: \t%d" % len(wrong_sameas))
    # print("#Error links injected: \t\t%d" % len(error_links))
    # print("#SameAs links to validate: \t%d" % V)
    # print("#False sameAs links found among the injected ones: \t%d\n" % len(inters))

    precision = len(inters) / len(error_links)
    recall = len(inters) / len(wrong_sameas) if len(wrong_sameas) != 0 else 0
    time = end_time - start_time

    print("Precision:\t", precision)
    print("Recall:\t\t", recall)
    print("Running time:\t %f s" % time)
    print()

    # write the result in a csv file
    fout.write(folder[:-1] + "," + str(precision) + "," + str(recall) + "," + str(time) + "\n")

fout.close()