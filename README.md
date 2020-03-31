# AI conference analysis

This repository is for analysing code release trends from NeurIPS 2019.

In future, it may extend to other analysis.

## Caveats

### NeurIPS 2019 code release

The analysis is imperfect. Some papers (49 out of 1428) don't make it all the way through the pipeline due to a missing file, failed text conversion or uncommon formatting. Some text information fails to be extracted correctly or detected at all. At a higher level, the analysis overlooks underlying factors that influence the decision to release code.

## Usage

## Quick replication 

Run `code_release_analysis.py` to replicate the analysis of NeurIPS 2019 code release. Requires `python >= 3.6`.

## Going deeper

See `environment.yml` for dependencies. The main ones are

- `python >= 3.6`
- `scrapy`
- `nltk`
- `scikit-learn`
- `spacy`
- `allennlp`

`bash code_release_pipeline.sh` will run the full pipeline to reproduce the analysis of NeurIPS 2019 code release. Getting the data and doing named entity recognition take a long time, so in practice you may want to run the steps separately.

## Sample results

```
Code release fraction for biggest publishers

1. Carnegie Mellon University (0.72, 76)
2. Stanford University (0.81, 74)
3. University of California (0.69, 62)
4. Google Research (0.58, 55)
5. Microsoft Research (0.76, 46)
6. MIT (0.8, 44)
7. Columbia University (0.73, 41)
8. Princeton University (0.44, 39)
9. Facebook AI Research (0.76, 37)
10. Tsinghua University (0.75, 36)
```
