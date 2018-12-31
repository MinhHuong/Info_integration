
from pipeline import PropertyExtraction

from xml.dom import minidom
import random
import io

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
		else:
			raise ValueError('%s entity of source Ontology already\
			 SameAs %s entity of target Ontology! ' %(key,value))

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


if __name__ == '__main__':

	no_erroneous = 400 # number of erroneous sameAs statements to be injected
	verbose = 0 # verbosity

	# filenames
	path_data_ref_001 = '../data/001/refalign.rdf'
	path_data_ref_002 = '../data/002/refalign.rdf'
	path_data_owl_000 = '../data/000/onto.owl'
	path_data_owl_001 = '../data/001/onto.owl'
	path_data_owl_002 = '../data/002/onto.owl'

	sameAs_001 = correct_sameAs(path_data_ref_001) #Dict
	sameAs_002 = correct_sameAs(path_data_ref_002) #Dict

	func000 = PropertyExtraction(filename=path_data_owl_000)#graph
	func001 = PropertyExtraction(filename=path_data_owl_001)#graph

	# get the random URI's subject
	random_source_001 = random_subject(func000.g,sameAs_001, check_refalign = True)
	random_target_001 = random_subject(func001.g, check_refalign = False)

	random_source_002 = random_subject(func000.g,sameAs_002, check_refalign = True)
	random_target_002 = random_subject(func001.g, check_refalign = False)

	# inject erroneous subjects in input graphs
	inject(path_data_ref_001,'../data/001/refalign_err_injected',random_source_001,random_target_001)
	inject(path_data_ref_002,'../data/002/refalign_err_injected',random_source_002,random_target_002)




