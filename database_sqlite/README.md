# Stree Map Data

## Generate the csv files

> first, run data.py to create the following csv files
> These files should not have header rows

    nodes.csv
    nodes_tags.csv
    ways.csv
    ways_nodes.csv
    ways_tags.csv


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
