import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import re
from db import Database

"""
    - Audit
    - Develop plan for Cleaning
    - Write code to clean
"""

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", 
            "Avenue", 
            "Boulevard", 
            "Drive", 
            "Court", 
            "Place", 
            "Square", 
            "Lane", 
            "Road", 
            "Trail", 
            "Parkway", 
            "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street"
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def parse_map(filename):

    north = None
    south = None
    east = None
    west = None

    shop_list = {}
    shop_types = {}
    tag_types = []
    with open(filename, "r") as handle:
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag == "node":
                name = None
                shop_type = None
                for tag in elem.iter("tag"):
                    k = tag.attrib["k"]
                    v = tag.attrib["v"]

                    if k not in tag_types:
                        print("{}={}".format(k, v))
                        tag_types.append(k)

                    if k == "shop" or k == "amenity":
                        shop_type = v

                    elif k == "name":
                        name = v

                if shop_type:
                    shop_types.setdefault(shop_type, 0)
                    shop_list.setdefault(shop_type, [])
                    shop_types[shop_type] += 1
                    if name not in shop_list[shop_type]:
                        shop_list[shop_type].append(name)
                    
    print("----- tags ------")
    tag_types.sort()
    for t in tag_types:
        print(t)

    print("----- shops ------")
    in_order = sorted( ((v,k) for k,v in shop_types.items()), reverse=True)
    for k, v in in_order:
        print("{}: {}".format(k, v))
        for name in shop_list[v]:
            print("    {}". format(name))


    print("North: {}".format(north))
    print("South: {}".format(south))
    print("East: {}".format(east))
    print("West: {}".format(west))



class TempLogger(object):

    def __init__(self):
        pass    

    def info(self, text):
        print(text)

    def debug(self, text):
        print(text)

class MapParser():
    
    def __init__(self):
        self._tag_types = {}
        self._logger = TempLogger()

    def _discover_tag_types(self, filepath):
        """
            Parses the XML and returns
            all of the tag types found
            with the count of each
        """
        tag_types = {}
        self._logger.info("Discovering Tag Types in %s" % filepath)
        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start",)):
                tag_type = elem.tag
                tag_types.setdefault(tag_type, 0)
                tag_types[tag_type] += 1
        return tag_types


    def _describe_tag_attributes(self, filepath, tag_type):
        """
            Pase the XML and reports the 
            attributes of the tag type
        """
        num_samples = 8
        attribute_counts = {}
        attribute_samples = {}

        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start",)):
                if elem.tag == tag_type:
                    for key, value in elem.attrib.items():
                        attribute_counts.setdefault(key, 0)
                        attribute_samples.setdefault(key, {})
                        attribute_counts[key] += 1
                        if value not in attribute_samples[key]:
                            attribute_samples[key].setdefault(value, 0)
                            attribute_samples[key][value] += 1

        print("  -- attributes for {} --".format(tag_type))
        for attribute, count in attribute_counts.items():
            print("  {}: {} num distinct values: {} ({})".format(attribute, 
                                                                 count, 
                                                                 len(attribute_samples[attribute].keys()),
                                                                 ", ".join(list(attribute_samples[attribute].keys())[:num_samples])))

    def _describe_tag_children(self, filepath, tag_type):
        """
            Pase the XML and reports the 
            child tags of the tag type
        """
        num_samples = 5
        tag_counts = {}

        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start",)):
                if elem.tag == tag_type:
                  for child_tag in elem:
                    tag_name = child_tag.tag
                    tag_counts.setdefault(tag_name, 0)
                    tag_counts[tag_name] += 1

        if tag_counts:
            print("  -- tags for {} --".format(tag_type))
            for tag_name, count in tag_counts.items():
                print("  {}: {}".format(tag_name, count))


    def clean_string(self, string):
        string = string.encode('utf-8')
        return string

    def clean_house_number(self, housenumber):
        fixes = { 
                  '5218;5216': '5218',
                  '1512;1514': '5212',
                  '400 Hf': '400',
                  '1718 A': '1718',
                  '1720 A': '1720',
                  '3139 Hf': '3139',
                  '2372 #130': '2372',
                  '802½': '802',
                  '425A': '425',
                  '212a': '212',
                  '709 1/2': '709',
                  '625 1/2': '625',
                }

        if housenumber in fixes:
            housenumber = fixes[housenumber]

        try:
            housenumber = int(housenumber)
        except ValueError:
            print(housenumber)
            return 0

        return housenumber

    def clean_postcode(self, postal_code):
        
        fixes = {
                    'LA 70116': '70116',
                    '70130-3890': '70130',
                    'LA 70117': '70117',
                }
        if postal_code in fixes:
            postal_code = fixes[postal_code]

        postal_code = int(postal_code)
        return postal_code
    

    def is_name_tag(self, tag_name):
        if tag_name == "name":
            return True
        if tag_name.startswith("name:"):
            return True


    def _identify_tags_steroids(self, filepath):
        """
            Identifies tags along with their parent heirarcy
        """
        tag_types = {}
        tag_types_ordered = []
        stack = []
        events = {}
        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start","end")):
                if event == "start":
                    stack.append(elem.tag)
                    tag_path = "/".join(stack)
                    tag_types.setdefault(tag_path, 0)
                    if tag_types[tag_path] == 0:
                        print(tag_path)
                        tag_types_ordered.append(tag_path)
                    tag_types[tag_path] += 1
                if event == "end":
                    stack.pop()
                    
        for item in tag_types_ordered:
            print("{} {}".format(item, tag_types[item]))

    def _identify_tags(self, filepath):
        """
            Use iterative parsing
            to identify all of the top-level
            tag types in the document
        """

        tag_types = {}
        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start",)):
                tag_types.setdefault(elem.tag, 0)
                tag_types[elem.tag] += 1

        pprint.pprint(tag_types)

    def _parse_node_tags(self, filepath, db):

        ignore_tags = ["gnis:feature_id", "created_by"]
        import_tags = []

        tag_counts = {}
        tag_values = {}
        with open(filepath, "r") as handle:
            for event, elem in ET.iterparse(handle, events=("start",)):
                if elem.tag == "node":
                    
                    node_data = {'id': elem.attrib['id'],
                                 'lat': elem.attrib['lat'],
                                 'lon': elem.attrib['lon'],
                                 'name': None,
                                 'description': None,
                                 'cuisine': None,
                                 'denomination': None,
                                 'shop': None,
                                 'amenity': None,
                                }
                    
                    node_names = {}
                    node_phones = {}
                    node_urls = {}
                    for child_tag in elem:
                        if child_tag.tag == "tag":

                            k = child_tag.attrib['k']
                            v = child_tag.attrib['v']

                            if k in ignore_tags:
                                continue

                            elif self.is_name_tag(k):
                                node_names[k] = self.clean_string(v)

                            elif k == "amenity":
                                node_data['amenity'] = self.clean_string(v)

                            elif k == "description":
                                node_data['description'] = self.clean_string(v)

                            elif k == "phone":
                                continue

                            elif k == "website":
                                continue
                
                            elif k == "shop":
                                node_data['shop'] = self.clean_string(v)
                                continue
                
                            elif k == "addr:housenumber":
                                house_number = self.clean_house_number(v)
                                continue

                            elif k == "addr:postcode":
                                house_number = self.clean_postcode(v)
                                continue

                            elif k == "addr:street":
                                continue

                            elif k == "opening_hours":
                                continue

                            elif k == "cuisine":
                                node_data['cuisine'] = self.clean_string(v)
                                continue

                            elif k == "denomination":
                                node_data['denomination'] = self.clean_string(v)
                                continue

                            tag_counts.setdefault(k, 0)
                            tag_counts[k] += 1

                            tag_values.setdefault(k, {})
                            tag_values[k].setdefault(v, 0)
                            tag_values[k][v] += 1

                    node_data['name'] = node_names.get('name', node_names.get('name:en'))
                    
                    if node_data['name']:
                        db.add_node(node_data)

        #for key, values in tag_values.items():
        #    print("{}".format(key))
        ##    for value, count in values.items():
        #        print("  {}: {}".format(value, count))


    def process_map(self, filepath, db):

        self._identify_tags_steroids("new_orleans_city")
        return
        self._parse_node_tags(filepath, db)
        return

        tag_types = self._discover_tag_types(filepath)

        for name, count in tag_types.items():
            print("{}: {}".format(name, count))
            self._describe_tag_attributes(filepath, name)
            #self._describe_tag_children(filepath, name)


if __name__ == "__main__":
    db = Database()
    db.connect(host="127.0.0.1",
               port=3306,
               database='udacity',
               username='root',
               password='')
    #db.test_connection()
    #db.execute("truncate table map_node;")
    #db.create_node_table()
    #db.test_connection()
    #db.add_node(None)

    mp = MapParser()
    mp.process_map("new_orleans_city", db)
    #mp.process_map("new_orleans_big", db)




