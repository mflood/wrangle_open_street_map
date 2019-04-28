#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script provided by Udacity

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "downloaded_maps/new_orleans_city.osm"  # Replace this with your osm file
SAMPLE_FILE = "new_orleans_city_sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'w') as output:
    output.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
    output.write("""<osm>\n  """)

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            s = ET.tostring(element, encoding='utf-8')
            s = "{}".format(s)
            output.write(s)

    output.write('</osm>')
