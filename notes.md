## 2020.03.18

- Run spider example: `scrapy runspider quotes_spider.py -o quotes.json`
- Made a bash script

Research questions

- What are the affiliations of authors for code vs. no code?
- Do the reviewers care? E.g. do they point out when there is (not) code?
- What sources of funding are there for papers with code vs. no code?
    - Acknowledgements would have this information

Working out author affiliation

- Best: retrieve all affiliations of all authors, and map these affiliations to commercial/non-commercial, geographic location, most associated state e.g. China, USA
- Proxy: extract affiliations of all authors via Google Scholar
    - Query Google Scholar with the author's name
    - Extract the top result and fetch the corresponding page
    - Extract the affiliation stated
- Proxy: extract affiliations of all authors via PDF
    - Requires more intelligent text processing
    - What tools already exist?

Extract affiliations of all authors via Google Scholar

- `scholarly` API is fantastic
- Problem: double up of names
- Solution: iterate names until a relevant `interests` is found
    - 'Artificial Intelligence', 'Learning', 'Neuroscience'
- Problem: double up of names AND a more relevant set of `interests` comes before the true author (AND more citations)
    - Well, we may just have to accept some error here. Or do data cleaning.
    - OR or, try to match the paper title in their list of pubs!
- Testing...
    - It is very slow
    - It would be faster, processing-wise, to read the PDFs

## 2020.03.20

- 
