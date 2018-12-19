import rdflib as rdf
import pprint as pp

path_data = '../data/'

#################
#   FUNCTIONS   #
#################

def parse_graph(input_file):
    '''
    Parse the RDF graph from the given input file
    :param input_file: the name of the .owl input file e.g. 000/onto.owl
    '''

    # parse the graph, may take some time
    g = rdf.Graph()
    g.parse(source=path_data + input_file, format='xml')

    # some statistics
    print('The RDF graph has', len(g), 'triples')

    # return the graph
    return g


def count_predicate_occurrences(predicates_objects, candidates):
    '''
    Count the number of times a predicate p is associated to a given subject s e.g.
    ex:a    rdf:type    ex:Person
    ex:a    ex:work_at  ex:School
    ex:a    ex:work_at  ex:Office
    ex:a    ex:work_at  ex:France
    Then the count should be: { "rdf:type" : 1, "ex:work_at": 3 }

    Besides from counting the number of occurrences of predicates,
    we should also update the total number of time it has appeared until now
    i.e. to update the total count in candidates

    :param predicates_objects: the list of tuples (predicate, object) associated to a subject
    :return: a dictionary where k = predicate and v = its number of occurrences
    '''

    # dictionary where k = predicate and v = the number of times p occurs (with a given subject)
    occurrences = {}
    for p_o in predicates_objects:
        p = p_o[0]

        # count the occurrences of a predicate p
        if p not in occurrences:
            occurrences[p] = 1
        else:
            occurrences[p] += 1

        # update the total count of p
        if p not in candidates:
            # if p not yet added to candidates,
            # initialize its total count to 1 and its functionality count to 0
            candidates[p] = [0, 1]
        else:
            # else, just increment its total count
            candidates[p][1] += 1

    return occurrences


def update_candidates(candidates, occurrences):
    '''
    Update the count of each candidate predicate.
    :param candidates: the dictionary candidates
    :param occurrences: the occurrences dictionary, where k = predicate p and v = number of occurrences of p
    :return: None
    '''

    # if a predicate appears only ONCE i.e. its number of occurrences = 1
    # update it in the dictionary of candidates by incrementing its count (1st element) by 1
    for p, count in occurrences.items():
        if count == 1:
            candidates[p][0] += 1 # update the functionality count


def filter_functional_properties(candidates, threshold=0.8):
    '''
    Filter out properties that are unlikely to be functional,
    by dividing functionality count by the total count of a predicate p.

    We then compare the obtained ratio with the threshold,
    if the ratio is >= the threshold, then p is possibly a functional property

    :param candidates: the candidates dictionary
    :param threshold: the functionality threshold
    :return:
    '''
    functional_properties = set()
    for p, counts in candidates.items():
        deg = counts[0]/counts[1]
        if deg >= threshold:
            functional_properties.add(p)
    return functional_properties


#####################
#   MAIN PIPELINE   #
#####################

# (1) parse the input file to have the RDF graph
g = parse_graph('000/onto.owl')


# a dictionary where k = predicate and v = 2-element list of (functionality count, total count)
# candidates is a dictionary where k = predicate p and v is a 2-element list where:
#   - the 1st element is the number of times p(s) gives only one output (functionality count)
#   - the 2nd element is the number of times p appears in the graph (total count)
candidates = {}

# just for test purposes
# i = 1

for s in g.subjects():
    # (2.1) count the number of occurrences of each predicate p of s
    predicates_occurrences = count_predicate_occurrences(g.predicate_objects(s), candidates)

    # (2.2) for those predicates that appear only ONCE, update the functionality count
    update_candidates(candidates, predicates_occurrences)

    # test with some examples only, instead of on the entire graph
    # to remove when we run for real
    # i += 1
    # if i >= 1:
    #     break

# (3) having the count of each predicate i.e. the number of times it associates one input to only one output
# compute the degree of functionality (a percentage?)
functional_properties = filter_functional_properties(candidates, threshold=0.8)

print('Number of functional properties:', len(functional_properties))