-- the data csv files need to be created
-- befgore this load script can be run
delete from node;
delete from node_tag;
delete from way;
delete from way_node;
delete from way_tag;

.mode csv

.import nodes.csv node
.import nodes_tags.csv node_tag
.import ways.csv way
.import ways_nodes.csv way_node
.import ways_tags.csv way_tag
