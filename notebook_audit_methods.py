"""
    Methods used by NewOrleansStreetMapWrangling.ipynb
"""
import pprint
import xml.etree.cElementTree as ET
import re


def identify_tags_fullpath(filepath):
    """
        Identifies tags along with their parent heirarchy
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
                    # print(tag_path)
                    tag_types_ordered.append(tag_path)
                tag_types[tag_path] += 1
            if event == "end":
                stack.pop()

    for item in tag_types_ordered:
        print("{0: <20} {1: >10}".format(item, tag_types[item]))


def audit_tag_keys(filepath, parent_tag):
    """
        parent_tag: way, node, relation

        Audit all the "k" attributes and put them into 4 buckets
        1. all lowercase and valid
        2. all lowercase with a ':' in the middle, and valid
        3. ones with bad characters
        4. others (none of the above)
    """

    lowercase_tags = {}
    lowercase_colon_tags = {}
    bad_char_tags = {}
    other_tags = {}

    regex_all_lower = re.compile(r'^([_a-z])*$')
    lower_colon = re.compile(r'^([_a-z])*:([_a-z])*$')
    problemchars = re.compile(r'[^_a-z]')

    with open(filepath, "r") as handle:
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag == parent_tag:
                for elem in elem.iterfind("tag"):
                    if elem.tag == "tag":
                        k_val = elem.attrib['k']
                        v_val = elem.attrib['v']
                        # print(k_val)
                        if regex_all_lower.match(k_val):
                            lowercase_tags.setdefault(k_val, set())
                            lowercase_tags[k_val].add(v_val)
                        elif lower_colon.match(k_val):
                            lowercase_colon_tags.setdefault(k_val, set())
                            lowercase_colon_tags[k_val].add(v_val)
                        elif problemchars.match(k_val):
                            bad_char_tags.setdefault(k_val, set())
                            bad_char_tags[k_val].add(v_val)
                        else:
                            other_tags.setdefault(k_val, set())
                            other_tags[k_val].add(v_val)

    return (lowercase_tags, lowercase_colon_tags, bad_char_tags, other_tags)

def print_example_entities(filepath, tag_key, max_results):
    """
        finds and prints up to max_results sample Nodes / Ways / Relations
        that have the specified tag key
    """
    with open(filepath, "r") as handle:
        num_examples_found = 0
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag in ("node", "relation", "way"):
                found_an_example = False
                example_dict = {}
                
                for child_tag in elem.iterfind("tag"):
                    if child_tag.tag == "tag":
                        k_val = child_tag.attrib['k']
                        v_val = child_tag.attrib['v']
                        
                        example_dict.setdefault(k_val, set())
                        example_dict[k_val].add(v_val)
                        
                        if k_val == tag_key:
                            found_an_example = True
                
                if found_an_example:
                    num_examples_found += 1
                    print("Example {}".format(elem.tag))    
                    pprint.pprint(example_dict)
                          
                    if max_results and (num_examples_found >= max_results):
                        # we have printed max_results so we are done
                        return



def get_all_streets(map_path, show_normal=True):
    """
        look at address:street values
        that match (or don't match) a street regex.
    """
    tag_key = "addr:street"

    value_counts = {}
    with open(map_path, "r") as handle:

        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag in ("node", "relation", "way"):

                value_dict = {}

                for child_tag in elem.iterfind("tag"):
                    k_val = child_tag.attrib['k']
                    v_val = child_tag.attrib['v']

                    if k_val == tag_key:
                        value_counts.setdefault(v_val, 0)
                        value_counts[v_val] += 1

    return value_counts



def print_entities_on_street(map_path, tag_key, tag_value, max_results):
    """
        finds and prints up to max_results sample Nodes / Ways / Relations
        that have the specified tag key with a certain value
        e.x. tag_key = street:add
             tag_value = "Bal of Square"
    """
    with open(map_path, "r") as handle:
        num_examples_found = 0
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag in ("node", "relation", "way"):
                found_an_example = False
                example_dict = {}

                # save atrributes too
                for key, value in elem.attrib.items():
                    key_name = "attribute: {}".format(key)
                    example_dict.setdefault(key_name, set())
                    example_dict[key_name].add(value)

                for child_tag in elem.iterfind("tag"):
                    if child_tag.tag == "tag":
                        k_val = child_tag.attrib['k']
                        v_val = child_tag.attrib['v']

                        example_dict.setdefault(k_val, set())
                        example_dict[k_val].add(v_val)

                        if k_val == tag_key and v_val == tag_value:
                            found_an_example = True

                if found_an_example:
                    num_examples_found += 1
                    print("Example {}".format(elem.tag))
                    pprint.pprint(example_dict)

                    if max_results and (num_examples_found >= max_results):
                        # we have printed max_results so we are done
                        return
                        # we have printed max_results so we are done
                        return
