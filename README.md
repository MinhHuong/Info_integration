# Information Integration project: Invalidating erroneous sameAs links

### Team members (by alphabetical order of lastnames):
- Billel GUERFA
- Armita KHAJEHNASSIRI
- Minh Huong LE NGUYEN
- Nafaa SI SAID

## TODO

- Review the refactored code of each module, namely `validator`, `injector`, `extractor`
- Improve the performance of the validator

## Pipeline
Syntax to call the validator:

`python pipeline source_graph target_graph val_graph threshold`

where `source_graph` should always be the reference ontology 000/onto.owl, 
`target_graph` is 00i/onto.owl where i != 0, 
`val_graph` is the refalign with **erroneous sameAs links injected in**, 
and `threshold` is the threshold over which a property can be considered functional.

If the parameters are not provided, the default values are assigned to each parameter.

The pipeline comprises of main steps:
1. Extracting the functional properties from source & target graph (`extractor` module)
2. Validating the sameAs links given in `val_graph`

**N.B.:** The injection of erroneous sameAs links (`injector` module) is done separately, 
out of the pipeline scope. To inject wrong sameAs links before invoking the pipeline, 
one should call:

`python injector.py source_path target_path refalign_path output_path num_error`

For example: `python code/injector.py data/000/onto/owl 
data/001/onto.owl data/001/refalign.rdf data/001/err_refalign.rdf 400`  
