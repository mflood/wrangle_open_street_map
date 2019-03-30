-- Run this after you have loaded the
-- data into sqlite3
-- to check that some data got into each table
select 'testing node';
select count(*) from  node;
select * from node limit 1;

select 'testing node_tag';
select count(*) from  node_tag;
select * from node_tag limit 1;

select 'testing way';
select count(*) from  way;
select * from way limit 1;

select 'testing way_node';
select count(*) from  way_node;
select * from way_node limit 1;

select 'testing way_tag';
select count(*) from  way_tag;
select * from way_tag limit 1;

