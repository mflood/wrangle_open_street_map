# wrangle\_open\_street\_map


> Matthew Flood
> 
> This is My project submission for Udacity's Data Analyst Nanodegree Data Wrangling course


## Environment Setup
> This project uses python 3.6.8 with pip 19.0.3
> 
> I used conda to manage the environment:

    conda env create -n wrangling_py368 python=3.6.8
    source activate wrangling_py368
    pip install pip==19.0.3
    pip install -r requirements.txt

## Downloading the data

>    New Orleans City
>     
[openstreetmap bounding box](https://www.openstreetmap.org/export#map=11/30.0326/-89.8826)
> 
[download](https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015)

    curl -o new_orleans_city.osm https://overpass-api.de/api/map?bbox=-90.2170,29.8633,-89.5482,30.2015
