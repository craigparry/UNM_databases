++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
README file for MappingCode 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
- The file mapping_processor.py is used to "map" or convert 
linked.art jsonld files to schema.org jsonld files. The file
is executable and can be run from the command line so long as
python3 is available. It has one positional argument, which is
the jsonld file for a linked.art "VisualItem" property or the
"HumanMadeObject" property. 

- An example of how to run the file is below:
./mapping_processor.py LinkedArt/the_farm.jsonld
