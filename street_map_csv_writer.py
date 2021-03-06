#!/usr/bin/env python
"""
    provides StreetMapCsvWriter object
    This object handles opening and writing
    to various csv files

"""

# -*- coding: utf-8 -*-
import csv
import codecs
import os.path
import sys

# This is what we're using for the wrangling course
NODES_FILENAME = "nodes.csv"
NODE_TAGS_FILENAME = "nodes_tags.csv"
WAYS_FILENAME = "ways.csv"
WAY_NODES_FILENAME = "ways_nodes.csv"
WAY_TAGS_FILENAME = "ways_tags.csv"

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']

class StreetMapCsvWriter():

    def __init__(self, add_csv_headers, output_directory):
        self._writers = {}
        self._filehandles = []
        self._add_csv_headers = add_csv_headers
        self._output_directory = output_directory
        self._num_nodes = 0
        self._num_node_tags = 0
        self._num_ways = 0

        self._setup_for_wrangling_course()

    def __del__(self):
        """
            destructor - cleanup open handles
        """
        for handle in self._filehandles:
            handle.close()

    def _make_output_path(self, filename):
        """
            append filename to output directory
        """
        return os.path.join(self._output_directory, filename)

    def _setup_for_wrangling_course(self):
        """
            create CSV writer for each record type
            used in the OSM project
        """
        self._add_writer('node', NODES_FILENAME, NODE_FIELDS)
        self._add_writer('node_tags', NODE_TAGS_FILENAME, NODE_TAGS_FIELDS)
        self._add_writer('way', WAYS_FILENAME, WAY_FIELDS)
        self._add_writer('way_nodes', WAY_NODES_FILENAME, WAY_NODES_FIELDS)
        self._add_writer('way_tags', WAY_TAGS_FILENAME, WAY_TAGS_FIELDS)

    def _add_writer(self, writer_name, filename, fieldlist):
        """
            Build a CSV writer identified by writer_name
        """
        
        # determine full output path
        filepath = os.path.join(self._output_directory, filename)


        codec = codecs.open(filepath, 'w', encoding='utf-8')
        self._filehandles.append(codec)
        writer = csv.DictWriter(codec, fieldlist)
        if self._add_csv_headers:
            writer.writeheader()
        self._writers[writer_name] = writer
        
    def _add_rows(self, writer_name, list_of_dictionaries):
        """
            Add a list of records to the CSV writer
            identified by writer_name
        """
        assert(isinstance(list_of_dictionaries, list))
        self._writers[writer_name].writerows(list_of_dictionaries)
        
    def _add_row(self, writer_name, dictionary):
        """
            Add a single record to the CSV writer
            identified by writer_name
        """
        assert(isinstance(dictionary, dict))
        self._writers[writer_name].writerow(dictionary)
        
    # Convenience functions
    #
    def add_node(self, node_dictionary):
        """
        Writes node data to the node csv writer

        The dictionary argument should match 'node'
        from schema.py

        e.g.
        {
          'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
          'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
          'changeset': 5288876
        }
        """
        self._num_nodes += 1
        if self._num_nodes % 100000 == 0:
            print("n: {}".format(self._num_nodes))
        self._add_row('node', node_dictionary)

    def add_node_tags(self, list_of_tag_dicts):
        """
           [
               {'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
            ]
        """
        self._num_node_tags += 1
        if self._num_node_tags % 100000 == 0:
            print("nt: {}".format(self._num_node_tags))
        self._add_rows('node_tags', list_of_tag_dicts)

    def add_way(self, way_dictionary):
        """
            {'id': 209809850,
             'user': 'chicago-buildings',
             'uid': 674454,
             'version': '1',
             'timestamp': '2013-03-13T15:58:04Z',
             'changeset': 15353317},
         """
        self._num_ways += 1
        if self._num_ways % 10000 == 0:
            print("w: {}".format(self._num_ways))
        self._add_row('way', way_dictionary)

    def add_way_nodes(self, list_of_waynode_dicts):
        """
              [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
        """
        self._add_rows('way_nodes', list_of_waynode_dicts)

    def add_way_tags(self, list_of_tag_dicts):
        """
              [
                  {'id': 209809850,
                   'key': 'street',
                   'type': 'addr',
                   'value': 'West Lexington St.'},
                  {'id': 209809850,
                   'key': 'street:name',
                   'type': 'addr',
                   'value': 'Lexington'},
               ]
        """
        self._add_rows('way_tags', list_of_tag_dicts)


if __name__ == '__main__':

    writer = StreetMapCsvWriter(add_csv_headers=True)
    writer.add_node({'id': 'honda', 'lat': 'blue'})
    writer.add_node_tags([{'id': 1, 'key': None}, {'id': 2, 'key': 13}, {'id': 3, 'key': 'rer'}])
