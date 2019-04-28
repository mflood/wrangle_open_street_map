# Loading Street Map Data into Sqlite

## Generate the csv files

> first, run `../process_map.sh` to create the following csv files
> These files should not have header rows

    ../generated_data/nodes.csv
    ../generated_data/nodes_tags.csv
    ../generated_data/ways.csv
    ../generated_data/ways_nodes.csv
    ../generated_data/ways_tags.csv


## Create the Database Tables  

> Run the following to (re) create the database

    sqlite3 new_orleans.db < drop_tables.sql
    sqlite3 new_orleans.db < create_tables.sql


## Import the csv files

> This will take a while.  Ony do this once!

    sqlite3 new_orleans.db < load_tables.sql

## Test the import

> Execute the SQL in 'test\_tables.sql' to get sample output and counts for each table

    sqlite3 new_orleans.db < test_tables.sql


## Use the database
> connect to the database:

    sqlite3 new_orleans.db

> run sql commands:

```
SQLite version 3.27.2 2019-02-25 16:06:06
Enter ".help" for usage hints.

sqlite> .tables
node      node_tag  way       way_node  way_tag

sqlite> .schema way_tag
CREATE TABLE way_tag (
    way_id INTEGER NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    tag_type TEXT,
    FOREIGN KEY (way_id) REFERENCES way(way_id)
);

sqlite> select tag_type, tag_key, count(*) from way_tag group by 1, 2 order by 3 desc limit 10;
regular|building|154204
addr|street|83853
addr|housenumber|83821
regular|highway|19268
tiger|county|15535
tiger|cfcc|15503
regular|name|12652
tiger|name_base|10881
tiger|name_type|10145
tiger|reviewed|9668

sqlite> .exit

```
