#!/bin/sh
mkdir -p generated_data
source activate wrangling_py368
python data.py
