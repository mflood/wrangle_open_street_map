# Wrangle Open Street Map: New Orleans

> Matthew Flood
>
> This is My project submission for Udacity's Data Analyst Nanodegree Data Wrangling course


## Environment Setup
> This project uses python 3.6.8 with pip 19.0.3
>
> I used conda to manage the environment:

    conda create -n wrangling_py368 python=3.6.8
    source activate wrangling_py368
    pip install pip==19.0.3
    pip install -r requirements.txt
    # make this environment available as a kernel in jupyter notebook
    conda install ipykernel

## Downloading the data

>    New Orleans City

[openstreetmap bounding box](https://www.openstreetmap.org/export#map=11/30.0326/-89.8826)
>
[download from overpass-api.de](https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015)

```bash
curl -o new_orleans_city.osm https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015
```

## Auditing the data

> You can follow my audit trail here: [NewOrleansStreetMapWrangling.html](NewOrleansStreetMapWrangling.html)
> or by launching this jupyter notebook
> make sure you source the conda env first so the right kernel will be available

```bash
source activate wrangling_py368
jupyter notebook wrangling_project.ipynb
```

> Change the kernel to wrangling\_py368

### Summary of Problems Encountered in the Map Data
> This is an overview of what was discovered during the audit

1. Abbreviated Street name components like "St." for "Street", "St." for Saint and "N" for "North"
2. Inconsistent capitalization of tag keys. Examples are "Payments" vs. "payments" and "NHD:FTYPE" vs "NHD:FType"
3. Extra data in street names, such as "3157 Gentilly Blvd #2019", which should just be "Gentilly Boulevard"
4. Completely incorrect data, like "Bal of Square" which should be "Banks Street"


## Generating CSV files and importing into SqLite

### Generating the CSV Files

We need to process the downloaded map data and create CSV files that can be loaded into a database.  You can run the following by hand, or invoke process_map.sh, which does the same thing:

```bash
# make the output directory
mkdir -p generated_data

# source the conda env
source activate wrangling_py368

# run data.py
python data.py
```

#### Importing into SqLite
Once `data.py` has run, the generated csv files will be in the `generated_data` folder.  You can then import the CSV files into SqLite by following the instructions in [database_sqlite/README.md](database_sqlite/README.md)


# Data overview and additional Ideas

### File Sizes

Downloaded Data Size

```
maps/new_orleans_city.osm ......... 373 MB
```

Generated CSV File Sizes

```
generated_data/nodes.csv .......... 145 MB
generated_data /nodes_tags.csv .... 4.6 MB
generated_data /ways.csv .......... 11 MB
generated_data /ways_nodes.csv .... 47 MB
generated_data /ways_tags.csv ..... 17 MB
```

SQLite Database

```
database_sqlite/charlotte.db ...... 195 MB MB
```

### Number of Nodes

```
sqlite> select count(*) from node;
```
```
1786106
```

### Number of Ways

```
sqlite> select count(*) from way;
```
```
189487
```

### Number of Unique Users

```
sqlite>
        select count(*)
        from (select distinct node_uid as uid
                from node
              union
              select distinct way_uid as uid
                from way) combined;
```
```
678
```

### Top 10 contributing Users

```sql
sqlite>
        select user, count(*)
         from (select
                      node_uid as uid
                    , node_user as user
                 from node
               union all
               select
                      way_uid as uid
                    , way_user as user
                 from way ) combined
        group by combined.uid, combined.user
        order by count(*) desc limit 10;
```
```
ELadner .................. 691640
Matt Toups ............... 611595
coleman_nolaimport ....... 348711
woodpeck_fixbot .......... 60712
Matt Toups_nolaimport .... 53337
Minh Nguyen_nolaimport ... 38517
ceseifert_nolaimport ..... 36319
Minh Nguyen .............. 10210
42429 .................... 7962
coleman .................. 6740
```


## Additional Data Exploration

### Top 10 appearing amenities

```sql
sqlite>
        select
            tag_value
          , count(*) as num
        from
        (
            select tag_value
              from node_tag
             where tag_key='amenity'
            union all
            select tag_value
              from way_tag
             where tag_key='amenity'
        )
        group by tag_value
        order by num desc
        limit 10;

```

```
place_of_worship ... 808
school ............. 495
restaurant ......... 387
parking ............ 376
kindergarten ....... 155
fast_food .......... 117
bar ................ 104
cafe ............... 103
fuel ............... 66
fire_station ....... 57
```

### Religions

```sql
sqlite>
        select
            tag_value
          , count(*) as num
        from
        (
            select tag_value
              from node_tag
             where tag_key='religion'
            union all
            select tag_value
              from way_tag
             where tag_key='religion'
        )
        group by tag_value
        order by num desc
```

```
christian ................ 776
jewish ................... 10
unitarian_universalist ... 1
```

### Religious Denominations

```sql
sqlite>
        select
            tag_value
          , count(*) as num
        from
        (
            select tag_value
              from node_tag
             where tag_key='denomination'
            union all
            select tag_value
              from way_tag
             where tag_key='denomination'
        )
        group by tag_value
        order by num desc
```

```
baptist ................... 340
methodist ................. 58
catholic .................. 51
lutheran .................. 25
roman_catholic ............ 13
pentecostal ............... 10
jehovahs_witness .......... 9
presbyterian .............. 8
episcopal ................. 5
mormon .................... 2
reform .................... 2
Church_of_Christ .......... 1
church_of_god_in_christ ... 1
greek_orthodox ............ 1
jewish .................... 1
orthodox .................. 1
protestant ................ 1
```

### Most popular cuisines

```sql
sqlite>
        select
              n1.tag_value
            , count(1) as num
         from node_tag n1
          inner join node_tag n2
          on n2.node_id = n1.node_id
          and n2.tag_value = 'restaurant'
        where n1.tag_key='cuisine'
        group by 1
        order by 2 desC
        limit 10
```

```
regional ..... 19
pizza ........ 12
american ..... 11
vietnamese ... 9
mexican ...... 8
seafood ...... 6
italian ...... 5
sandwich ..... 5
asian ........ 4
chinese ...... 4
```


### Which streets cross Bourbon Street
```sql
select
     cross_street_tags.tag_value as cross_street_name
-- , main_street_nodes.way_id
-- , main_street_nodes.node_id
-- , cross_street_nodes.way_id
-- , node.node_lat
-- , node.node_lon
from way_node as main_street_nodes

-- all the way_nodes that cross bourbon street
inner join way_node as cross_street_nodes
   on cross_street_nodes.node_id = main_street_nodes.node_id
      -- don't join bourbon street to itself
  and cross_street_nodes.way_id != main_street_nodes.way_id
-- get the node details
inner join node
  on node.node_id = cross_street_nodes.node_id
-- find the cross street name
inner join way_tag cross_street_tags
 on cross_street_tags.way_id = cross_street_nodes.way_id
 and cross_street_tags.tag_key = 'name'
where main_street_nodes.way_id = (
        select way_id 
          from way_tag 
         where tag_key = 'name' 
           and tag_value like 'Bourbon Street')
order by node.node_lat
, node.node_lon;
```

```
Carondelet Street
Canal Street
Canal St Streetcar
Canal St Streetcar
Canal Street
Iberville Street
Bienville Street
Conti Street
Saint Louis Street
Toulouse Street
Saint Peter Street
Orleans Avenue
Saint Ann Street
Dumaine Street
Saint Philip Street
Ursulines Avenue
Governor Nicholls Street
Barracks Street
Esplanade Avenue
Esplanade Avenue
Pauger Street
Kerlerec Street
```

## Ideas for Additional Improvements

> One improvement to the data would be to remove any data associated with "fixme" tags.  The benefit would be less noise in the data, but the drawback would be a more incomplete data set.
> 
```
sqlite> select tag_key
              , count(*) 
        from node_tag 
        where tag_key like '%FIX%' group by 1;
```
```
fixme|25
```

> Another improvement would be to standardize the date formats of tag_values.  For instance, the 'start_date' tag:

```
sqlite> select tag_value 
          from node_tag 
         where tag_key like 'start_date'
         order by 1;
```

```
1803
1856
1856-02-09
1862
1893
1894
1897
1899
1906
1938
1938
1943-11-10
1955
1983
1983
1984
1987
1991
1992-05-20
1995-03-19
2003-06
2008
2010
```

> One drawback of standardizing the start_date would be that we might not have the information of the actual day, and so using a default of, say , January 1, might be misleading to people.


