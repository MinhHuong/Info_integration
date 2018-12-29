import rdflib as rdf
import pprint as pp


class extractProperties(object):

    def __init__(self,filename,verbos=0,threshold = 0.8):
        self.g = rdf.Graph().parse(source= filename , format='xml')
        self.candidates = None
        self.verbos = verbos
        self.threshold = threshold
        self.functional_properties = None

    def build(self):

        if self.verbos == 2:
            print('building...!')

        self.candidates = {}
        self.functional_properties = set()


        for s in self.g.subjects():
            # (2.1) count the number of occurrences of each predicate p of s
            predicates_occurrences = self.count_predicate_occurrences(self.g.predicate_objects(s))
            if self.verbos==1:
                print(candidates)
                break

            # (2.2) for those predicates that appear only ONCE, update the functionality count
            self.update_candidates(predicates_occurrences)

        # (3) having the count of each predicate i.e. the number of times it associates one input to only one output
        # compute the degree of functionality (a percentage?)
        self.filter_functional_properties()

        if self.verbos == 2: 
            print('functional_properties: ',self.functional_properties)




    def count_predicate_occurrences(self,predicates_objects):
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
            if p not in self.candidates:
                # if p not yet added to candidates,
                # initialize its total count to 1 and its functionality count to 0
                self.candidates[p] = [0, 1]
            else:
                # else, just increment its total count
                self.candidates[p][1] += 1

        return occurrences


    def update_candidates(self, occurrences):
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
                self.candidates[p][0] += 1 # update the functionality count



    def filter_functional_properties(self):
        '''
        Filter out properties that are unlikely to be functional,
        by dividing functionality count by the total count of a predicate p.
        We then compare the obtained ratio with the threshold,
        if the ratio is >= the threshold, then p is possibly a functional property
        :param candidates: the candidates dictionary
        :param threshold: the functionality threshold
        :return:
        '''
        for p, counts in self.candidates.items():
            deg = counts[0]/counts[1]
            if deg >= self.threshold:
                self.functional_properties.add(p)



if __name__ == '__main__':

    path_data_000 = '../data/000/onto.owl'
    path_data_001 = '../data/001/onto.owl'

    func000 = extractProperties(path_data_000)
    func000.build()
    print(len(func000.functional_properties))

    func001 = extractProperties(path_data_001,threshold=1)
    func001.build()
    print(len(func001.functional_properties))
