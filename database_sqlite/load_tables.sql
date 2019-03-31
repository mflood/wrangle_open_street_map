-- the data csv files need to be created
-- befgore this load script can be run
delete from node;
delete from node_tag;
delete from way;
delete from way_node;
delete from way_tag;

.mode csv

.import ../generated_data/nodes.csv node
.import ../generated_data/nodes_tags.csv node_tag
.import ../generated_data/ways.csv way
.import ../generated_data/ways_nodes.csv way_node
.import ../generated_data/ways_tags.csv way_tag
