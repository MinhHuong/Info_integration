# some header here
import rdflib as rdf
from onto_graph import OntoGraph
import injector as inj


def detect_false_sameas(same_as, g1, g2):
    """
    Given some sameAs links, checks if U1 sameAs U2 and p is a common property of U1 and U2
    if p(U1, x) AND p(U2, y) and if x == y then the sameAs property is valid
    valid sameAs properties are added to a new dictionnary true_sameAs

    :param same_as: a list of same-as links as tuple
    :param g1:
    :param g2:
    :return:
    """
    true_sameAs = {}
    wrong_sameas_count = 0

    # for each sameAs statements
    for link in same_as:
        U1, U2 = link[0], link[1]
        common_props = get_common_prop(U1, U2, g1.graph, g2.graph)  # All the common properties between U1 and U2

        FPcount = 0  # count the number of functional properties
        SameFPcount = 0  # count the number of functional properties with x == y
        for p in common_props:
            if p in g1.functional_properties and p in g2.functional_properties:  # functional properties filtering
                FPcount = FPcount + 1  # we found a functional property
                objs1 = list(g1.graph.objects(rdf.URIRef(U1), p))
                objs2 = list(g2.graph.objects(rdf.URIRef(U2), p))
                if len(objs1) == 1 and len(objs2) == 1 and objs1[0] == objs2[0]:
                    SameFPcount = SameFPcount + 1  # we found a functional property validating x == y

        # retrieve the true sameAs
        if FPcount > 0:
            if SameFPcount / FPcount >= 0.5:
                if U1 not in true_sameAs:
                    true_sameAs[U1] = U2
            else:
                wrong_sameas_count += 1  # also want to have the number of wrong sameAs detected

    # print("True same as ratio : ", len(true_sameAs) / len(same_as))

    return (len(true_sameAs), wrong_sameas_count)


def get_common_prop(U1, U2, G1, G2):
    """
    This function gets the common properties between 2 URIs subjects in 2 different ontologies
    return the rdf property
    """
    pred_obj1 = set([p for p, o in list(G1.predicate_objects(rdf.URIRef(U1)))])
    pred_obj2 = set([p for p, o in list(G2.predicate_objects(rdf.URIRef(U2)))])
    return pred_obj1.intersection(pred_obj2)


############################
# For testing purpose only #
############################
if __name__ == '__main__':
    print('Testing the validator...')

    # what we want: inject a number of erroneous sameAs links to a refalign file
    # by using URI's from that refalign's folder AND the source ontology

    # create the graphs, then extract its functional properties
    g_0 = OntoGraph('../data/000/onto.owl')
    g_0.extract_func_properties()

    g_1 = OntoGraph('../data/001/onto.owl')
    g_1.extract_func_properties()

    to_validate = inj.extract_sameas('../data/001/err_refalign.rdf')

    detect_false_sameas(same_as=to_validate, g1=g_0, g2=g_1)
