from xml.dom import minidom
import random
import sys as sys
from onto_graph import OntoGraph


def create_wrong_sameas(target_graph, source_graph, output_path, target_refalign_path, no_error):
    """
    The main method that wraps all the procedures of wrong sameAs statements injection

    :param target_graph:  the ontology of a folder != 000 (that folder must contain a refalign)
    :param source_graph:  the reference ontology in 000/
    :param output_path:             where to save the graph with erroneous sameAs links injected
    :param target_refalign_path:    the gold standard refalign.rdf in the same folder as target_path
    :param no_error:                number of erroneous links # TODO extend to a ratio
    :return:                        None
    """
    # extract same-as statements from gold standard in refalign
    same_as = extract_sameas(target_refalign_path)

    # get random URIs
    random_source = random_uri(graph=source_graph.graph, no_erroneous=no_error,
                               dict_sameas=same_as, check_refalign=True)
    random_target = random_uri(graph=target_graph.graph, no_erroneous=no_error,
                               dict_sameas=same_as, check_refalign=False)

    # inject erroneous in target_graph
    inject(target_refalign_path, output_path, random_source, random_target)


def inject(input_path, output_path, source, target):
    """
    Inject erroneous sameAs statements.
    We use minidom to parse refalign and to inject erroneous sameAs links.
    The erroneous sameAs links will be saved in output_path

    :param input_path:  path to refalign
    :param output_path: path to save refalign with injected errors
    :param source:      a list containing random subjects from source ontology (000)
    :param target:      a list containing random subjects from target ontology (001/ 002)
    :return:            None
    """

    assert (len(source) == len(target))
    size = len(source)
    doc = minidom.parse(input_path)  # open existing file for parsing

    alignment = doc.getElementsByTagName('Alignment')[0]
    for i in range(size):
        data = doc.createElement('map')
        alignment.appendChild(data)
        cell = doc.createElement('Cell')
        data.appendChild(cell)

        cons = doc.createElement('entity1')
        cons.setAttribute('rdf:resource', source[i])
        cell.appendChild(cons)

        cons = doc.createElement('entity2')
        cons.setAttribute('rdf:resource', target[i])
        cell.appendChild(cons)

        relation = doc.createElement('relation')
        text = doc.createTextNode('=')
        relation.appendChild(text)
        cell.appendChild(relation)

        measure = doc.createElement('measure')
        measure.setAttribute('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#float')
        text = doc.createTextNode('1.0')
        measure.appendChild(text)
        cell.appendChild(measure)

    # doc.writexml(open(name+'.xml','w'))
    doc = doc.toprettyxml()

    # save file
    text_file = open(output_path, 'w')
    text_file.write(doc)
    text_file.close()


def extract_sameas(path_refalign):
    """
    This method parses the refalign file with minidom parser for XML.

    :param path_refalign:   path to the refalign gold standard'../data/001/refalign.rdf'
    :return:                A dictionary that keeps correct SameAs Links
                            between the source & target ontology defined in refalign
    """
    same_as = {}
    xmldoc = minidom.parse(path_refalign)
    entity1_onto_source = xmldoc.getElementsByTagName('entity1')
    entity2_onto_target = xmldoc.getElementsByTagName('entity2')

    for i in range(len(entity1_onto_source)):
        key = entity1_onto_source[i].attributes['rdf:resource'].value
        value = entity2_onto_target[i].attributes['rdf:resource'].value
        if key not in same_as:
            same_as[key] = value
        # else:
        #     raise ValueError(
        #         '%s entity of source Ontology already in SameAs %s entity of target Ontology!'
        #         % (key, value))

    return same_as


def random_uri(graph, no_erroneous, dict_sameas=None, check_refalign=True, verbose=0):
    """
    Select random URI subject from a given graph
    TODO Include URIs from the objects also

    :param graph:           the ontology graph
    :param no_erroneous:    number of random URIs to extract from the graph
                            TODO maybe fix a ratio instead of a constant
    :param dict_sameas:     TODO add information
    :param check_refalign:  TODO add information
    :param verbose:         level of verbosity
    :return:                a list of randomly selected subjects from an ontology
                            (that we get as 'input')
    """

    random_subject = []

    '''
    graph.subjects() : subjects in an rdf triple - type: <class 'generator'>
    We want to select 400 (no_erroneous) random subjects not existing as a key of 
    sameAs dictionary
    In order not to save all subjects in a list and then randomly select from them, 
    we use sorted()
    '''

    for subject in sorted(graph.subjects(), key=lambda k: random.random()):
        if verbose == 1:
            print(str(subject))
            break

        if check_refalign:
            if subject not in dict_sameas:
                random_subject.append(str(subject))
        else:
            random_subject.append(str(subject))

        if len(random_subject) == no_erroneous:
            break

    return random_subject


############################
# For testing purpose only #
############################
if __name__ == '__main__':
    print('Running the injector...')

    # what we want: inject a number of erroneous sameAs links to a refalign file
    # by using URI's from that refalign's folder AND the source ontology

    # extract arguments from the command line
    if len(sys.argv) < 6:
        print("Syntax: python injector.py source_graph target_graph refalign_path output_path num_error")
        sys.exit(0)

    source_path = sys.argv[1]
    target_path = sys.argv[2]
    refalign_path = sys.argv[3]
    output_path = sys.argv[4]
    num_error = int(sys.argv[5])

    # create the graphs, no need to extract functional properties
    g_source = OntoGraph(source_path)
    g_target = OntoGraph(target_path)

    # inject wrong sameAs
    create_wrong_sameas(target_graph=g_target,
                        source_graph=g_source,
                        output_path=output_path,
                        target_refalign_path=refalign_path,
                        no_error=num_error)

    print("The result is found in", output_path)
