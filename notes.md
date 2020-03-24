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

PDF download

- Only 1205 papers downloaded
- Because one of them is missing (checked the webpage):
- Added `HTTPError` handling to `download_pdf.py`
    ```
    Failed to write 9724-visual-sequence-learning-in-hierarchical-prediction-networks-and-primate-visual-cortex.pdf:
    HTTP Error 404: Not Found
    ```
- Done - all except that one paper downloaded

## 2020.03.23

Narrowing down affiliation entities

- Ok, so we have named entity recognition going
- Current filters:
    - Label is ORG or PER
    - Text starts with upper case letter (gets rid of e.g. email addresses)
        - Hmm, seems like a better filter is `'@' not in ent.label_`
    - 'school', 'lab', 'department' -> reject
        - This is bad. For example, 'Tencent AI Lab'. Although I don't know if that was picked up in the first place for the example I'm looking at.
- So I've realised this NER is actually inadequate. It didn't pick up "Tencent AI Lab" or "MIT-IBM Watson AI Lab" (though it did get "MIT" by itself)
- I'm currently joining up the lines of text and removing the `\n`. However, I think the NER task would be easier if I feed line-by-line.

Looking at alternative NER

- AllenNLP looks SOTA, but is compute-heavy
- I have the intuition that a simple NER would be sufficient - just need to try a few and pick the best one.
- Ok, this seems good.

Preprocessing

- Remove any numbers at the start or end of words. Hopefully no organisations have numbers...
    - Nope, Data61 is in there (8333, 9410)
    - Ok, so how can we distinguish this...
    - Maybe just remove numbers at the beginning. From two examples I've tested, the NER seems to be fine recognising names despite the numbers. Besides, we don't need names for now, just affiliations.
- Remove non-alphanumeric symbols
    - 9704 is an example
    - `for char in string;if not char.isalnum()`
- Bugger, in some papers the affiliations are at the bottom of the page and hence past the abstract, which was my assumed limit. What to do?
    - For now, at least, I'm just going to give up on these cases. I hope we can get a strong enough sample without them. I've glanced at a few paper txts and most of them seem to have affiliations above the abstract.

Other considerations

- How to avoid org tags in the title?
    - Look for the first PER recognition first
    - Ok no, this doesn't always apply. Sometimes the org is before the first person.

Running full affiliation extraction
