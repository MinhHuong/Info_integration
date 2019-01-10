# some header here
import rdflib as rdf
from onto_graph import OntoGraph
import injector as inj
import utils as ut
import time as tm
import random as rd


def invalidate_sameas(sameas, g1, g2, depth):
    """
    Another version of code that invalidates erroneous sameAs links

    :param sameas: a list of same-as links (as tuple) from which we should detect false sameAs
    :param g1: graph 1
    :param g2: graph 2
    :param depth: depth i.e. number of times we want to go deep into validating the similarity of URI's
    :return: list of false same-as links
    """
    wrong_sameas = set()

    for link in sameas:
        u1, u2 = link[0], link[1]
        p = rd.random()
        if p >= 0.5:
            wrong_sameas.add(link)

        # if not ut.validate_link(u1, u2, g1, g2, depth=depth):
        #     wrong_sameas.add(link)

    return wrong_sameas

