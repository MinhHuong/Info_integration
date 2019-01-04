
from pipeline import PropertyExtraction

from xml.dom import minidom
import random
import io
import rdflib as rdf

def inject(input_path,output_path,source,target): #source and target are 2 lists
	"""
	Inject erroneous sameAs statements.
	We use minidom to parse refalign and to inject erroneous sameAs links.

	:param input_path: path to refalign
	:param output_path: path to save refalign with injected errors
	:param source: a list containing random subjects from source ontology (000)
	:param target: a list containing random subjects from target ontology (001/ 002)
	:return: None
	"""

	assert (len(source) == len(target))
	size = len(source)
	doc = minidom.parse(input_path) # open existing file for parsing

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

	#doc.writexml(open(name+'.xml','w'))

	doc = doc.toprettyxml()

	# save file
	text_file = open(output_path+".rdf", "w")
	text_file.write(doc)
	text_file.close()


def correct_sameAs(path_refalign):
	"""
	This method parses the refalign file with minidom parser for XML.

	:param path_refalign: ex '../data/001/refalign.rdf'
	:return: A dictionary that keeps correct SameAs Links between
	ontologies (source) and (target) defined in refalign
	"""
	sameAs = {}
	xmldoc = minidom.parse(path_refalign)
	entity1_onto_source = xmldoc.getElementsByTagName('entity1')
	entity2_onto_target = xmldoc.getElementsByTagName('entity2')

	for i in range(len(entity1_onto_source)):
		key = entity1_onto_source[i].attributes['rdf:resource'].value
		value = entity2_onto_target[i].attributes['rdf:resource'].value
		if key not in sameAs:
			sameAs[key] = value
		#else:
			#raise ValueError('%s entity of source Ontology already\
			 #SameAs %s entity of target Ontology! ' %(key,value))

	return sameAs


def random_subject(graph,dict_sameAs={},check_refalign=True,verbose=0):
	"""

	:param graph:
	:param dict_sameAs:
	:param check_refalign:
	:param verbose:
	:return: a list of randomly selected subjects
	from an ontology (that we get as 'input')
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
			if subject not in dict_sameAs:
				random_subject.append(str(subject))
		else:
			random_subject.append(str(subject))

		if len(random_subject) == no_erroneous:
			break

	return random_subject


def detect_false_sameAs(sameAs, PE1, PE2):
	"""
	Given some sameAs links, checks if U1 sameAs U2 and p is a common property of U1 and U2
	if p(U1, x) AND p(U2, y) and if x == y then the sameAs property is valid
	valid sameAs properties are added to a new dictionnary true_sameAs
	"""
	true_sameAs = {}
	for U1, U2 in sameAs.items():
		common_props = get_common_prop(U1, U2, PE1.g, PE2.g)#All the common properties between U1 and U2
		
		FPcount = 0 #count the number of functional properties
		SameFPcount = 0 #count the number of functional properties with x == y
		for p in common_props:
			if p in PE1.functional_properties and p in PE2.functional_properties: #functional properties filtering
				FPcount = FPcount +1 #we found a functional property
				objs1 = list(PE1.g.objects(rdf.URIRef(U1), p))
				objs2 = list(PE2.g.objects(rdf.URIRef(U2), p))
				if len(objs1) == 1 and len(objs2) == 1 and objs1[0] == objs2[0]:
					SameFPcount = SameFPcount +1 #we found a functional property validating x == y
				#print(SameFPcount, FPcount)
		#print(SameFPcount, FPcount)
		if( FPcount > 0 and SameFPcount / FPcount >=  0.5):
			if U1 not in true_sameAs:
				true_sameAs[U1] = U2	
	print("True same as ratio : ", len(true_sameAs)/len(sameAs))

	return true_sameAs


def get_common_prop(U1, U2, G1, G2):
	"""
	This function gets the common properties between 2 URIs subjects in 2 different ontologies
	return the rdf property
	"""
	pred_obj1 = set([p for p,o in list(G1.predicate_objects(rdf.URIRef(U1)))])
	pred_obj2 = set([p for p,o in list(G2.predicate_objects(rdf.URIRef(U2)))])
	return pred_obj1.intersection(pred_obj2)
	

if __name__ == '__main__':

	no_erroneous = 400 # number of erroneous sameAs statements to be injected
	#verbose = 0 # verbosity

	# filenames
	path_data_ref_001 = '../data/001/refalign.rdf'
	path_data_ref_002 = '../data/002/refalign.rdf'
	path_data_ref_err_001 = '../data/001/refalign_err_injected.rdf'
	path_data_ref_err_002 = '../data/002/refalign_err_injected.rdf'
	path_data_owl_000 = '../data/000/onto.owl'
	path_data_owl_001 = '../data/001/onto.owl'
	path_data_owl_002 = '../data/002/onto.owl'

	func000 = PropertyExtraction(filename=path_data_owl_000, threshold = 0.6)#graph
	func001 = PropertyExtraction(filename=path_data_owl_001, threshold = 0.6)#graph
	func002 = PropertyExtraction(filename=path_data_owl_002, threshold = 0.6)#graph

	func000.build()
	func001.build()
	func002.build()

	sameAs_001 = correct_sameAs(path_data_ref_001) #Dict
	sameAs_002 = correct_sameAs(path_data_ref_002) #Dict
	sameAs_err_001 = correct_sameAs(path_data_ref_err_001)
	sameAs_err_002 = correct_sameAs(path_data_ref_err_002)

	detect_false_sameAs(sameAs_002, func000, func002)

	# get the random URI's subject
	# random_source_001 = random_subject(func000.g,sameAs_001, check_refalign = True)
	# random_target_001 = random_subject(func001.g, check_refalign = False)
	#
	# random_source_002 = random_subject(func000.g,sameAs_002, check_refalign = True)
	# random_target_002 = random_subject(func001.g, check_refalign = False)
	#
	# # inject erroneous subjects in input graphs
	# inject(path_data_ref_001,'../data/001/refalign_err_injected',random_source_001,random_target_001)
	# inject(path_data_ref_002,'../data/002/refalign_err_injected',random_source_002,random_target_002)
