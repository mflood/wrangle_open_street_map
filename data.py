#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
To do so you will parse the elements in the OSM XML file, transforming them from document format to
tabular format, thus making it possible to write to .csv files.  These csv files can then easily be
imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the
cerberus library we can validate the output against this schema to ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
  and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they and they should be ignored and kept as part of
  the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.

The final return value for a "node" element should look something like:

{'node': {'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
       'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
      'changeset': 5288876},
 'node_tags': [{'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'name',
                'value': "Shelly's Tasty Freeze",
                'type': 'regular'}]}

### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element

The final return value for a "way" element should look something like:

{'way': {'id': 209809850,
         'user': 'chicago-buildings',
         'uid': 674454,
         'version': '1',
         'timestamp': '2013-03-13T15:58:04Z',
         'changeset': 15353317},
 'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
 'way_tags': [{'id': 209809850,
               'key': 'housenumber',
               'type': 'addr',
               'value': '1412'},
              {'id': 209809850,
               'key': 'street',
               'type': 'addr',
               'value': 'West Lexington St.'},
              {'id': 209809850,
               'key': 'street:name',
               'type': 'addr',
               'value': 'Lexington'},
              {'id': '209809850',
               'key': 'street:prefix',
               'type': 'addr',
               'value': 'West'},
              {'id': 209809850,
               'key': 'street:type',
               'type': 'addr',
               'value': 'Street'},
              {'id': 209809850,
               'key': 'building',
               'type': 'regular',
               'value': 'yes'},
              {'id': 209809850,
               'key': 'levels',
               'type': 'building',
               'value': '1'},
              {'id': 209809850,
               'key': 'building_id',
               'type': 'chicago',
               'value': '366409'}]}
"""

import csv
import pprint
import re

import xml.etree.cElementTree as ET

# for schema validation
import cerberus
import schema

OSM_PATH = "downloaded_maps/new_orleans_city.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

expected = ["Street",
            "Avenue",
            "Court",
            "Drive",
            "Road",
            "Boulevard",
            "Place",
            "Lane",
            "Circle",
            "Cove",
            "Arcade",
            "Way",
            "Walk",
            "Highway",
            "Parkway",
            "Alley",
            "Plaza",
            "Trace"]


to_fix = {"St": "Street",
          "St.": "Street",
          "Ave": "Avenue",
          "Pkwy": "Parkway",
          "Hwy": "Highway",
          "Blvd": "Boulevard",
          "Dr": "Drive",
          "Ave.": "Avenue",
          "Pky": "Parkway"}

fullname_mapping = {"Banks": "Banks Street",
                    "Regent Street #C": "Regent Street",
                    "Dumaine": "Dumaine Street",
                    "Magazine Street;Magazine St": "Magazine Street",
                    "Magazine": "Magazine Street",
                    "Rosa PARK": "Rosa Park",
                    "Severn": "Severn Avenue",
                    "St. Peter": "Saint Peter Street",
                    "3157 Gentilly Blvd #2019": "Gentilly Boulevard",
                    "Marais": "Marais Street",
                    "Royal": "Royal Street",
                    "Canal Street at Bourbon": "Canal Street",
                    "General Taylor": "General Taylor Street",
                    "Gretna Blvd Ste A": "Gretna Boulevard",
                    "Manhattan Boulevard Building": "Manhattan Boulevard",
                    "Saint Charles Avenue, Suite 114-351": "Saint Charles Avenue",
                    "1227 Tulane Ave": "Tulane Avenue",
                    "621 Canal Street": "Canal Street",
                    "Westgrove PARK": "Westgrove Park",
                    "George 'Nick' Connor Drive": "George Nick Connor Drive",
                    "Bal of Square": "Banks Street",
                   }

def is_street_name(tag_key):
    """
        untility method to identify street addresses
    """
    return (tag_key == "addr:street")

street_type_re = re.compile(r'(.*) (\b\S+\.?)$', re.IGNORECASE)
def fix_street_name(value):
    """
        Normalize street names so they are more consistent
    """

    # trim any leading and trailing whitespace
    value = value.strip()

    # patch full items that are borked
    value = fullname_mapping.get(value, value)

    # match against street regex
    match = street_type_re.match(value)
    if match:
        #continue
        first_path = match.group(1)
        street_type = match.group(2)
        street_type = to_fix.get(street_type, street_type)

        value = "{} {}".format(first_path, street_type)

        beginnings = {'N ': 'North',
                      'S ': 'South',
                      'E ': 'East',
                      'W ': 'West',
                      'St ': 'Saint',
                      'St. ': 'Saint'}
        for k, v in beginnings.items():
            start_string = "{} ".format(k)
            if value.startswith(k):
                value = value.replace(k, v, 1)

        # any St or St. that still remain are 'Saint'
        value.replace('St ', 'Saint ')
        value.replace('St. ', 'Saint ')

    return value



lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def get_key_parts(full_key):
    """
        for keys with ':', returns first part and then everything else
        for keys without ':', returns 'regular' and then the full_key
    """
    colon_pos = full_key.find(':')

    base_type = 'regular'
    key = full_key

    if colon_pos >= 0:
        base_type = full_key[:colon_pos]
        key = full_key[colon_pos + 1:]

    return (base_type, key)

def shape_element(element,
                  node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):
    """
        Clean and shape node or way XML element to Python dict
    """

    # child <tag> elements are processed the same for both <node> and <way> elements
    #
    tags = []
    if element.tag in ('node', 'way'):
        # process the <way><tag> / <node><tag> elements
        #
        for tag in element.iter("tag"):

            # Force key to lowercase
            full_key = tag.attrib['k'].lower()
            value = tag.attrib['v']

            if is_street_name(full_key):
                value = fix_street_name(value)

            base_type, key = get_key_parts(full_key)

            tag_dict = {
                'id': element.attrib.get('id'),
                'key': key,
                'type': base_type,
                'value': value,
            }
            tags.append(tag_dict)

    if element.tag == 'node':

        # Process the attributes in the <node> element
        #
        node_attribs = {}
        for attribute in ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']:
            node_attribs[attribute] = element.attrib.get(attribute)

        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':

        # Process the attributes in the <way> element
        #
        way_attribs = {}
        for attribute in ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']:
            way_attribs[attribute] = element.attrib.get(attribute)

        # Process the <way><nd> elements
        #
        way_nodes = []
        position = 0
        for nd in element.iter("nd"):
            node_dict = {
                'id': element.attrib.get('id'),
                'node_id': nd.attrib.get('ref'),
                'position': position,
            }
            position += 1
            way_nodes.append(node_dict)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
        Yield element if it is the right type of tag
    """

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """
        Raise ValidationError if element does not match schema
    """
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.items())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        raise Exception(message_string.format(field, error_string))


# ================================================== #
#               Main Function                        #
# ================================================== #

def process_map(file_in, validate):
    """
        Iteratively process each XML element and write to csv(s
    """
    from street_map_csv_writer import StreetMapCsvWriter

    writer = StreetMapCsvWriter(add_csv_headers=False,
                                output_directory='generated_data')

    validator = cerberus.Validator()

    for element in get_element(file_in, tags=('node', 'way')):
        el = shape_element(element)
        if el:
            if validate is True:
                validate_element(el, validator)

            if element.tag == 'node':
                writer.add_node(el['node'])
                writer.add_node_tags(el['node_tags'])
            elif element.tag == 'way':
                writer.add_way(el['way'])
                writer.add_way_nodes(el['way_nodes'])
                writer.add_way_tags(el['way_tags'])

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)

