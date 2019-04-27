# wrangle\_open\_street\_map

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
[download](https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015)

```bash
curl -o new_orleans_city.osm https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015
```

## Auditing the data

> You can follow my audit trail by launching this jupyter notebook
>
>     jupyter notebook wrangling_project.ipynb
>
> Change the kernel to wrangling\_py368
### Here are the findings:
>
>
>

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

### Religios Denominations

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

