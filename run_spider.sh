#!/usr/bin/bash

SPIDER_FILE=$1
OUT_FILE=$2

rm -i ${OUT_FILE}
scrapy runspider ${SPIDER_FILE} -o ${OUT_FILE}
