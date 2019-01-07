import editdistance as ed
import dateutil.parser as dp


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

    LENGTH_THRESHOLD = 20
    LENTH_RATIO_THRESHOLD = 2

    # if s1 or s2 is too long (> 20 characters), return 1 (ignore non-sense text)
    if len(s1) >= LENGTH_THRESHOLD or len(s2) >= LENGTH_THRESHOLD:
        return 1

    # if s1 or s2 is empty, return 0
    if len(s1) == 0 or len(s2) == 0:
        return 0

    # if one string is too long wrt the other, return 1 (ratio = 2)
    if (len(s1) > len(s2) and len(s1) / len(s2) >= LENTH_RATIO_THRESHOLD) \
            or (len(s2) > len(s1) and len(s2) / len(s1) >= LENTH_RATIO_THRESHOLD):
        return 0

    # sim = ed.eval(s1, s2)  # uncomment to use Levenshtein
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

    # return date1 == date2


def synval(obj1, obj2, is_date=False):
    """
    Evaluate the similarity/equality of two objects o1 and o2.
    - If o1 and o2 are strings, employ string matching similarity measures
    (Jaro, Levenshtein, cosine similarity, etc.), return false if the strings are too long
    - If o1 and o2 are dates, parse them and compare
    if they both refer to the same date (but in different formats)
    - If o1 and o2 are URI's, evaluate if they can be sameAs in some sense (pretty tough)

    :param obj1: an object o1
    :param obj2: an object o2
    :param is_date: if both are a date
    :return: True if they are similar, False otherwise
    """

    # constants
    URI_PREFIX = "http"  # URI prefix
    SIM_THRESHOLD = 0.75

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
    if o1.startswith(URI_PREFIX) and o2.startswith(URI_PREFIX):
        return True

    # if both are strings
    if not o1.startswith(URI_PREFIX) and not o2.startswith(URI_PREFIX):
        if is_date:  # if o1 and o2 are dates
            return check_same_date(o1, o2)
        else:  # else, compute string similarity
            # a case that happens a lot and we can cheat somehow...
            if (o1 == "M" and o2 == "Male") or (o1 == "Male" and o2 == "M") or \
                    (o1 == "F" and o2 == "Female") or (o1 == "Female" and o2 == "F"):
                return True

            # otherwise, do thing transparently
            sim = compute_string_similarity(o1, o2)
            return sim >= SIM_THRESHOLD

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
