"""utils.py: utility methods, mostly used to verify the similarity of two arbitrary objects/strings"""

import editdistance as ed
import dateutil.parser as dp
import rdflib as rdf

__authors__ = "Billel Guerfa, Armita Khajehnassiri, Minh-Huong Le-Nguyen, Nafaa Si Said"


def jaro(s, t):
    """
    DISCLAIMER: this is not my code, I copied it from https://rosettacode.org/wiki/Jaro_distance#Python
    Compute the similarity between two strings using the Jaro algorithm.

    :param s: string s
    :param t: string t
    :return: the Jaro similarity measure between s and t
    """
    s_len = len(s)
    t_len = len(t)

    if s_len == 0 and t_len == 0:
        return 1

    match_distance = (max(s_len, t_len) // 2) - 1

    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    for i in range(s_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, t_len)

        for j in range(start, end):
            if t_matches[j]:
                continue
            if s[i] != t[j]:
                continue
            s_matches[i] = True
            t_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0

    k = 0
    for i in range(s_len):
        if not s_matches[i]:
            continue
        while not t_matches[k]:
            k += 1
        if s[i] != t[k]:
            transpositions += 1
        k += 1

    return ((matches / s_len) +
            (matches / t_len) +
            ((matches - transpositions / 2) / matches)) / 3


def compute_string_similarity(s1, s2):
    """
    Computes the similarity between two strings by using different methods,
    depending on the nature of the strings to be compared.

    :param s1: string s1
    :param s2: string s2
    :return: similarity measure of s1 and s2 (float in [0., 1.])
    """

    lenght_threshold = 20
    length_ratio_threshold = 2

    # if s1 or s2 is too long (> 20 characters), return 1 (ignore non-sense text)
    if len(s1) >= lenght_threshold or len(s2) >= lenght_threshold:
        return 1

    # if s1 or s2 is empty, return 0
    if len(s1) == 0 or len(s2) == 0:
        return 0

    # if one string is too long wrt the other, return 1 (ratio = 2)
    if (len(s1) > len(s2) and len(s1) / len(s2) >= length_ratio_threshold) \
            or (len(s2) > len(s1) and len(s2) / len(s1) >= length_ratio_threshold):
        return 0

    # sim = ed.eval(s1, s2) / max(len(s1), len(s2))  # uncomment to use Levenshtein
    sim = jaro(s1, s2)

    return sim


def check_same_date(d1, d2):
    """
    Checks if 2 strings refer to the same date disregard the format of each
    :param d1: date 1
    :param d2: date 2
    :return: True if they are the same date, False otherwise
    """
    date1 = dp.parse(timestr=d1)
    date2 = dp.parse(timestr=d2)

    # maybe only compare day and month, disregard year
    return date1.day == date2.day and date1.month == date2.month


def synval(obj1, obj2, is_date=False, g1=None, g2=None, depth=1):
    """
    Evaluate the similarity/equality of two objects o1 and o2.
    - If o1 and o2 are strings, employ string matching similarity measures
    (Jaro, Levenshtein, cosine similarity, etc.), return false if the strings are too long
    - If o1 and o2 are dates, parse them and compare
    if they both refer to the same date (but in different formats)
    - If o1 and o2 are URI's, evaluate if they can be sameAs in some sense (pretty tough)

    :param obj1:    an object 1
    :param obj2:    an object 2
    :param is_date: if both are a date
    :param g1:      the graph containing object 1
    :param g2:      the graph containing object 2
    :param depth:   the depth of URIs sub-validation
    :return: True if they are similar, False otherwise
    """

    # constants
    uri_prefix = "http"  # URI prefix
    sim_threshold = 0.75

    # string value of the objects
    o1, o2 = obj1.toPython(), obj2.toPython()

    # return immediately if their string values are the same
    if o1 == o2:
        return True

    # check type, if they are not both string, then return True
    # TODO very naive, to improve
    if type(o1) is not str or type(o2) is not str:
        return True

    # if they are both URI's
    # TODO check if they are really sameAs (recursive call to validator?...)
    if o1.startswith(uri_prefix) and o2.startswith(uri_prefix):
        if depth <= 0:
            return True
        return validate_link(obj1, obj2, g1, g2, depth-1)
        # return True

    # if both are strings
    if not o1.startswith(uri_prefix) and not o2.startswith(uri_prefix):
        if is_date:  # if o1 and o2 are dates
            return check_same_date(o1, o2)
        else:  # else, compute string similarity
            # a case that happens a lot and we can cheat somehow...
            if (o1 == "M" and o2 == "Male") or (o1 == "Male" and o2 == "M") or \
                    (o1 == "F" and o2 == "Female") or (o1 == "Female" and o2 == "F"):
                return True

            # otherwise, do thing transparently
            sim = compute_string_similarity(o1, o2)
            return sim >= sim_threshold

    # if one is an URI and the other is not, return True
    # TODO this is actually naive, they can still refer to the same object
    return True


def find_intersection(s1, s2):
    """
    Manual code to find intersection of 2 sets,
    where each set contains tuples of URIRef

    :param s1: set 1
    :param s2: set 2
    :return: the intersected set
    """
    result = set()

    for link in s1:
        u1, u2 = link[0], link[1]
        for _link in s2:
            _u1, _u2 = _link[0].toPython(), _link[1].toPython()
            # a link is valid in both direction so we need to do cross-comparison
            if (u1 == _u1 and u2 == _u2) or (u1 == _u2 and u2 == _u1):
                result.add(link)

    return result


def validate_link(u1, u2, g1, g2, depth=1):
    """
    Validates a sameAs links

    :param u1:      URIRef object
    :param u2:      URIRef object
    :param g1:      graph containing u1
    :param g2:      graph containing u2
    :param depth:   depth of URIs sub-validatiom
    :return:        False if the link is definitely false, otherwise True
                    (returning True doesn't think this link is absolutely True,
                    it simply means we cannot conclude otherwise)
    """

    common_props = get_common_prop(u1, u2, g1.graph, g2.graph)  # set of common properties of u1 and u2
    for p in common_props:
        if p in g1.functional_properties and p in g2.functional_properties:
            o1 = list(g1.graph.objects(subject=rdf.URIRef(u1), predicate=p))
            o2 = list(g2.graph.objects(subject=rdf.URIRef(u2), predicate=p))
            if len(o1) == 1 and len(o2) == 1:  # reinforce the functionality property
                is_date = "date_of_birth" in p.toPython()
                if not synval(o1[0], o2[0], is_date, g1, g2, depth=depth):
                    return False
    return True


def get_common_prop(U1, U2, G1, G2):
    """
    This function gets the common properties between 2 URIs subjects in 2 different ontologies
    return the rdf property
    """
    pred_obj1 = set([p for p, o in list(G1.predicate_objects(rdf.URIRef(U1)))])
    pred_obj2 = set([p for p, o in list(G2.predicate_objects(rdf.URIRef(U2)))])
    return pred_obj1.intersection(pred_obj2)
