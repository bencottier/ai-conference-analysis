#!/usr/bin/bash

PDF_DIR='./data/neurips_2019/pdf'
TXT_DIR='./data/neurips_2019/txt'

for FILE in "$PDF_DIR"/*
do
    echo ${FILE}
    pdf2txt.py ${FILE} > ${FILE//pdf/txt}
done
