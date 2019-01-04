import rdflib as rdf
import extractor as ext


class OntoGraph:

    def __init__(self, graph_path):
        """

        :param graph_path:
        """
        # the parsed graph
        self.graph = rdf.Graph().parse(source=graph_path, format='xml')

        # list of functional properties extracted from the given graph
        # TODO we can even extract properties right here if we like to
        self.functional_properties = []

    def extract_func_properties(self, threshold=0.8):
        """
        Extracts functional properties from this graph

        :param threshold:
        :return:
        """
        self.functional_properties = ext.extract_properties(self.graph, threshold)


############################
# For testing purpose only #
############################
if __name__ == '__main__':
    # create an ontology
    g = OntoGraph('../data/000/onto.owl')

    # extract its functional properties
    g.extract_func_properties(threshold=0.5)

    # check
    print('Number of functional properties:', len(g.functional_properties))
