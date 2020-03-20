#!/usr/bin/bash

rm ./code_stat.json
scrapy runspider code_stat.py -o code_stat.json
