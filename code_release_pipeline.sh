#!/usr/bin/bash

DATA_DIR="./data/neurips_2019"
PDF_DIR="${DATA_DIR}/pdf"
TXT_DIR="${DATA_DIR}/txt"
OUTPUT_DIR="./out/neurips_2019"
METADATA_FILE="${OUTPUT_DIR}/papers_metadata.json"
OUTPUT_FILE="${OUTPUT_DIR}/affiliations.json"
RESULTS_FILE="${OUTPUT_DIR}/code_rankings.txt"

printf "\nScraping metadata\n"
bash run_spider.sh neurips_2019_papers_spider.py ${METADATA_FILE}

printf "\nDownloading PDFs\n"
python download_pdf.py -m ${METADATA_FILE} -o ${PDF_DIR}

printf "\nConverting PDF to text\n"
mkdir -p ${TXT_DIR}
bash pdf2txt.sh ${PDF_DIR}

printf "\nExtracting affiliations from texts\n"
python affiliations_ner.py -m ${METADATA_FILE} -d ${TXT_DIR} -o "${OUTPUT_FILE}"

printf "\nAnalysing affiliations\n"
python code_release_analysis.py -i ${OUTPUT_FILE} > ${RESULTS_FILE}

printf "\nDone\n"
