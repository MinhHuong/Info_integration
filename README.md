# Information Integration project
## Invalidating erroneous sameAs links

### Team members (by alphabetical order of lastnames):
- Billel GUERFA
- Armita KHAJEHNASSIRI
- Minh Huong LE NGUYEN
- Nafaa SI SAID

### Pipeline
# Information Integration project: Invalidating erroneous sameAs links

### Team members (by alphabetical order of lastnames):
- Billel GUERFA
- Armita KHAJEHNASSIRI
- Minh Huong LE NGUYEN
- Nafaa SI SAID

## Pipeline

### 1 - Extraction of (likely) functional properties
For the first task, we need to extract the (most likely) funtional properties from a given RDF graph, by computing the **degree of functionality** of each predicate.

Let `G` be the RDF graph. The **degree of functionality** is computed as follows:
 
**(1)** For each subject `s` in `G`, we look at every predicate/property `p` associated to `s` and count the number of times `p` is associated to `s`.

For example, given those triples of a subject `ex:person`:

``	ex:person	rdf:type 	ex:Teacher``
``	ex:person	rdf:work_at	ex:School``
``	ex:person	rdf:work_at	ex:Office``
``	ex:person	rdf:work_at	ex:France``

The resulting count should be a dictionary : `{ "rdf:type": 1, "rdf:work_at": 3 }`

**(2)** We then count the number of times a predicate `p`, given an input `s`, only gives **one output** `o` . We call this type of counts the **functionality count** i.e. the number of times `p` behaves like a functional property.

At the end of this counting step, we should have a dictionary named `candidates` where the key is a predicate `p` and the value is a 2-element list where:

- the first element is the **functionality count** i.e. the number of times `p` only gives one output `o` for a given input `s`
- the second element is the **total count** i.e. the number of times `p` appears in the entire graph `G`

The degree of functionality of a predicate `p`p equals to the ratio of  (**functionality count of p / total count of p**). If this ratio is greate or equal to a threshold (defined by us), we say that `p` is functional, and vice-versa.

The goal of this step is to extract functional properties from `G`; that is, properties having the degree of functionality >= a threshold.

A skeleton of code has been implemented in `extract_properties.py`.

### 2 - Invalidate sameAs links

(not yet any idea because I'm craving for a holiday)
