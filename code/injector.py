from xml.dom import minidom
import random
import sys as sys
from onto_graph import OntoGraph


def create_wrong_sameas(target_graph, source_graph, output_path, target_refalign_path, ratio):
    """
    The main method that wraps all the procedures of wrong sameAs statements injection

    :param target_graph:  the ontology of a folder != 000 (that folder must contain a refalign)
    :param source_graph:  the reference ontology in 000/
    :param output_path:             where to save the graph with erroneous sameAs links injected
    :param target_refalign_path:    the gold standard refalign.rdf in the same folder as target_path
    :param ratio:                   Ratio of erroneous sameAs links injected (as an integer eg. 40 --> 40%)
    :return:                        None
    """
    # extract same-as statements from gold standard in refalign
    same_as = extract_sameas(target_refalign_path)

    # compute the no_errors from percentage(ratio)
    no_error = int((len(same_as) * ratio)/100)

    # get random URIs
    random_dict_uri = random_uri(graph_source=source_graph.graph,
                                 graph_target=target_graph.graph,
                                 no_erroneous=no_error,
                                 dict_sameas=same_as)

    # inject erroneous in target_graph
    inject(target_refalign_path, output_path, random_dict_uri)


def inject(input_path, output_path, random_dict_uri):
    """
    Inject erroneous sameAs statements.
    We use minidom to parse refalign and to inject erroneous sameAs links.
    The erroneous sameAs links will be saved in output_path

    :param input_path:      path to refalign
    :param output_path:     path to save refalign with injected errors
    :param random_dict_uri: TODO add information
    :return:                None
    """

    size = len(random_dict_uri)
    doc = minidom.parse(input_path) # open existing file for parsing

    alignment = doc.getElementsByTagName('Alignment')[0]
    for i in range(size):
        data = doc.createElement('map')
        alignment.appendChild(data)
        cell = doc.createElement('Cell')
        data.appendChild(cell)

        cons = doc.createElement('entity1')
        cons.setAttribute('rdf:resource', list(random_dict_uri.keys())[i]) # random choice from source onto
        cell.appendChild(cons)

        cons = doc.createElement('entity2')
        cons.setAttribute('rdf:resource', list(random_dict_uri.values())[i]) # random choice from target onto
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

    return same_as


def random_uri(graph_source, graph_target, no_erroneous, dict_sameas):
    """

    :param graph_source:    the ontology graph_source
    :param graph_target:    the ontology graph_target
    :param no_erroneous:    number of random URIs to extract from the graphs
    :param dict_sameas:     Dictionary of correct sameAs links from refalign
    :return:                A dictionary containing random "uri"s from source onto as key
                            and random "uri"s from target onto --> to be injected in refalign
    """

    random_dict_uri = {}

    '''
    graph.subject_objects() : "uri"s in an rdf triple (subjects and objects) - type: <class 'generator'>
    We want to select (no_erroneous) random source uri not existing as a key of 
    sameAs dictionary and (no_erroneous) target uri not existing as value of sameAs dict
    '''

    for uri_source, uri_target in zip(sorted(graph_source.subject_objects(), key=lambda k: random.random()),
                                      sorted(graph_target.subject_objects(), key=lambda k: random.random())):
        # Only take those "uri"s that are of type URIRef. (didn't make sense for string values)
        if 'URIRef' in str(type(uri_source[1])) and 'URIRef' in str(type(uri_target[1])):
            if 'URIRef' in str(type(uri_source[0])) and 'URIRef' in str(type(uri_target[0])):
                rand_uri_source = random.choice([uri_source[0], uri_source[1]])
                rand_uri_target = random.choice([uri_target[0], uri_target[0]])
                # Checking that we already do not have this random tuple in gold standard (refalign)
                if rand_uri_source in dict_sameas: 
                    if rand_uri_target != dict_sameas[rand_uri_source]:
                        random_dict_uri[rand_uri_source] = rand_uri_target
                else:
                    random_dict_uri[rand_uri_source] = rand_uri_target

                # create no more random tuples than asked for
                if len(random_dict_uri) == no_erroneous:
                    break

    if len(random_dict_uri) == no_erroneous:
        return random_dict_uri
    else:
        raise ValueError('Could not create the percentage of erroneous links that were asked !')


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
    ratio = float(sys.argv[5])

    # create the graphs, no need to extract functional properties
    g_source = OntoGraph(source_path)
    g_target = OntoGraph(target_path)

    # inject wrong sameAs
    create_wrong_sameas(target_graph=g_target,
                        source_graph=g_source,
                        output_path=output_path,
                        target_refalign_path=refalign_path,
                        ratio=ratio)

    print("The result is found in", output_path)
