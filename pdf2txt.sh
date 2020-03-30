#!/usr/bin/bash

PDF_DIR=$1

for FILE in "$PDF_DIR"/*
do
    echo ${FILE}
    pdf2txt.py ${FILE} > ${FILE//pdf/txt}
done
