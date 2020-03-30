# ML conference analysis

This repository is for analysing code release trends from NeurIPS 2019.

In future, it may extend to other analysis.

## Caveats

### NeurIPS 2019 code release

The analysis is imperfect. Some papers (104 out of 1428) don't make it all the way through the pipeline due to a missing file, failed text conversion or uncommon formatting. Some text information fails to be extracted correctly or detected at all. At a higher level, the analysis overlooks underlying factors that influence the decision to release code.

## Installation

See `environment.yml` for dependencies. The main ones are

- `python >= 3.6`
- `scrapy`
- `nltk`
- `scikit-learn`
- `spacy`
- `allennlp`

`bash code_release_pipeline.sh` will run the full pipeline necessary to reproduce the analysis of NeurIPS 2019 code release. Getting the data and doing named entity recognition take a long time, so in practice you may want to run the steps separately.

## Sample results

```
Lowest fraction of papers with code

1. Cognitive Computing Lab (0.17, 6)
2. California Institute of Technology (0.2, 5)
3. NEC Corporation (0.25, 4)
4. The University of Tokyo (0.25, 4)
5. Google Inc. (0.25, 4)
6. University of Minnesota (0.25, 12)
7. Baidu Research (0.29, 7)
8. Intel AI Lab (0.33, 3)
9. Universitat Pompeu Fabra (0.33, 3)
10. University at Buffalo (0.33, 3)

Highest fraction of papers with code

1. University College London (1.0, 16)
2. University of Amsterdam (1.0, 11)
3. PSL Research University (1.0, 10)
4. Texas A&M University (1.0, 9)
5. Université Paris (1.0, 9)
6. University of British Columbia (1.0, 9)
7. Imperial College London (1.0, 8)
8. Aalto University (1.0, 8)
9. University of Tokyo (1.0, 8)
10. National University of Singapore (1.0, 7)
```
