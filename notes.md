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

- Lessons learned:
    - Some entities still have numbers attached to the front
    - Should remove duplicates...or should I? Maybe the proportion of certain institutions has an effect.
    - Other school-type words like "College". But maybe I should just keep all of those rather than try to catch all the cases?
    - Some weird unicode which we may want to clean. I think it's stuff like the 'ff' single character. Would just be a rule-based postprocess.
    - Some titles still made it in, e.g. "Lipschitz Constrained Convolutional Networks" and "Hamiltonian Neural Networks"
- Error - maybe the line with just a space character? I've had this before, associated with an empty line being included
    ```
    ['Uncertainty on Asynchronous Time Event Prediction',
    '',
    'Marin Biloš∗, Bertrand Charpentier∗, Stephan Günnemann',
    '',
    'Technical University of Munich, Germany',
    '',
    '������� ��������� ���������������������',
    '']

    ['Uncertainty on Asynchronous Time Event Prediction',
    '',
    'Marin Biloš, Bertrand Charpentier, Stephan Günnemann',
    '',
    'Technical University of Munich, Germany',
    '',
    '  ',
    '']
    (O) Uncertainty (O) on (O) Asynchronous (O) Time (O) Event (O) Prediction 
    (B-PER) Marin (L-PER) Biloš (O) , (B-PER) Bertrand (L-PER) Charpentier (O) , (B-PER) Stephan (L-PER) Günnemann 
    (B-ORG) Technical (I-ORG) University (I-ORG) of (L-ORG) Munich (O) , (U-LOC) Germany 
    Traceback (most recent call last):
    File "ner.py", line 140, in <module>
    File "ner.py", line 129, in main
        has_code = metadata['code']
    File "ner.py", line 99, in extract_affiliations
        for word, tag in zip(result["words"], result["tags"]):
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/predictors/sentence_tagger.py", line 29, in predict
        return self.predict_json({"sentence" : sentence})
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/predictors/predictor.py", line 65, in predict_json
        return self.predict_instance(instance)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/predictors/predictor.py", line 181, in predict_instance
        outputs = self._model.forward_on_instance(instance)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/models/model.py", line 124, in forward_on_instance
        return self.forward_on_instances([instance])[0]
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/models/model.py", line 153, in forward_on_instances
        outputs = self.decode(self(**model_input))
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/models/crf_tagger.py", line 182, in forward
        embedded_text_input = self.text_field_embedder(tokens)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/modules/text_field_embedders/basic_text_field_embedder.py", line 131, in forward
        token_vectors = embedder(*tensors, **forward_params_values)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/modules/token_embedders/elmo_token_embedder.py", line 95, in forward
        elmo_output = self._elmo(inputs, word_inputs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/modules/elmo.py", line 171, in forward
        bilm_output = self._elmo_lstm(reshaped_inputs, reshaped_word_inputs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/modules/elmo.py", line 607, in forward
        token_embedding = self._token_embedder(inputs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/torch/nn/modules/module.py", line 532, in __call__
        result = self.forward(*input, **kwargs)
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/modules/elmo.py", line 347, in forward
        character_ids_with_bos_eos, mask_with_bos_eos = add_sentence_boundary_token_ids(
    File "/home/ben/miniconda3/envs/nlp/lib/python3.8/site-packages/allennlp/nn/util.py", line 1288, in add_sentence_boundary_token_ids
        sequence_lengths = mask.sum(dim=1).detach().cpu().numpy()
    IndexError: Dimension out of range (expected to be in range of [-1, 0], but got 1)
    ```

## 2020.03.27

Debugging

- Let's start with the actual error
    - Ok, there's a line with a bunch of weird question symbols
    - These symbols get removed, leaving whitespace
    - (?) The whitespace causes an empty sequence for the NER (because it tokenizes)
    - The algorithm assumes there are at least two dimensions in the mask, but there is only one. Perhaps due to a squeeze operation.
    - So these symbols, are they meaningful? If so, we should think about what to do with them. If not, perhaps the solution is to apply `strip()` a second time at the end of preprocessing, so that if the preprocessing removed all characters on the line, any leftover whitespace is reduced to an empty string, then gets ignored.
    - Let's look at the source material: 9445
        - Strange. It seems to be the email addresses. When I copy that from the PDF viewer, then paste it in a plain text window, it just has the question mark symbols.
    - **FIXED**
- We should keep the file name in the output JSON so that we can trace any issues back to the source material easily.
    - **FIXED**
- Picking up parts of titles as entities
    - The thing is, we know what the actual title is from the metadata! So if an entity is a substring of the title, get that outta there. Seems very unlikely that a true entity will completely overlap a title, but you never know...
    - Oh dear...every time I say something: "Amazon Search" is an entity and part of a title. 9482.
    - I think we can still disambiguate, but the one case we may have to forfeit is: something is in the title, AND an affiliation, AND that affiliation is the first one.
    - Wait, wait. We know what the actual title is. We can use that knowledge to figure out which lines in the file the title occurs on. It will be a bit fancy to account for multi-line titles, but it's doable. Then, we ignore entities that occur on a title line.
        - I think we'll need to add the line number to the entity data that we pass to postprocessing.
    - Ok. Consider this rule: entity is a substring of title AND entity is in the first or second non-empty line.
        - Are there any three-line titles? To be really thorough we need a way of measuring the number of lines a title spans.
- Ok just saw an email address get in. Need removal based on '@'! Surely that's a safe one...
- 

Data processing

- Seems safe to ignore detections with length less than 3. Can't _think_ of any relevant entities that are two letters long. Three letters, yes - MIT, IBM. But I might not have thought of those before seeing the initial results, so I can't trust my judgement of two letters.
- Sometimes non-standard symbols are clues! Consider: "UT Austin Amazon". In the paper, the entities were separated by a symbol, but we got rid of that.
    - I think the compromise then is to flank non-standard symbols with spaces, so that they are not captured as part of the entity, but can be used by the recogniser to separate entities. There is a risk that the unusual (or unknown) token will throw it off - we'll see.
        - To track this: 9538

SUPER COOL IDEA

- We have the headers. We know whether the paper provided code or not. Supervised learning!
- Train a binary classifier to predict the whether a paper provided code or not, based on the header, abstract, or the whole paper. Though the whole paper may become almost cheating if it can find code urls. That's not the reason this model would be valuable to me.
- Could even run a simple model, e.g. logistic regression, on the processed entities.
- Analyse which features most influence the prediction
    - Maybe via the examples with most extreme probability?

Related task that would help current task

- Classify an entity as industry or academia
- A thorough database/web crawl solution would be more accurate than an ML solution

Error

- For the paper that was not available: 9724 / index 1205
- Added an "ignore" list for these cases

## 2020.03.29

Debugging

- Ok, what's left?
- Numbers still appear at the start of entities
- Picking up parts of titles as entities
    - This seems top priority

Removing spurious title entities

- From last time, our best strategy seems to be: computing which lines the title occurs on by matching to the title in the metadata, then ignoring those lines in the NER process.
- Uncertainty: do titles always exactly match between paper and metadata?
    - We can factor out capitalization and whitespace either side.
    - Could there be unicode that makes it different?
        - Yes: e.g. 8322 has fi vs. ﬁ
        - To deal with this, we can systematically check the unicodes in the JSON file and create a lookup table for replacement
    - Could there be slightly different wording?
        - Yes: 9693
            - Metadata: 'TAB-VCR: Tags and Attributes based VCR Baselines'
            - Data: 'TAB-VCR: Tags and Attributes based Visual Commonsense Reasoning Baselines'
        - Edit distance may not even work here. The abbreviation and the full thing are very different.
        - Depends how common this is. If it's rare enough, we will manually correct.
    - We can check this by running the title function by itself for every paper, printing out the indices found
    - 9708 failed; no header lines.
        - Oh dear...the title starts with 'Abstract'.
        - **FIXED**
    - Failure cases
        - 9659: no whitespace. The whole file is one continuous line.
        - 9657: titles are paraphrases
        - 9654: special apostrophe character converted as &#39 (metadata) vs. 0
        - 9636: different wording (metadata title is a substring) 
        - 9624: special apostrophe character vs. missing
        - 9580: extra space
            - 'General E(2) - Equivariant Steerable CNNs'
            - 'General E(2) Equivariant Steerable CNNs'
        - 9566: word 'neural' missing from metadata
        - 9547: special apostrophe character vs. missing
        - 9545: double space in metadata
        - 9527: they changed the name of the algorithm! Rand-NSG vs. DiskANN. Rest of title is the same.
    - Ok, too many failure cases. Two options:
        - Abandon this method entirely
        - Ignore when it fails, just to increase the probability that a title is not caught.
    - Either way we should consider a different approach.
- Old approach, for reference
    ```python
    def find_title(header_lines, title):
        title_indices = list()
        title_started = False
        title_ = title.strip().lower()
        for i, line in enumerate(header_lines):
            line_ = line.strip().lower()
            if len(line_) < 1:
                continue
            # Title may be broken over multiple lines
            if not title_started and title_.startswith(line_):
                title_started = True
                title_indices.append(i)
                if line_ == title_:
                    break
            elif title_started and title_.endswith(line_):
                title_indices.append(i)
                break
            elif title_started and line_ in title_:
                title_indices.append(i)
        if len(title_indices) == 0:
            warnings.warn(f'Could not match title "{title}"')
        return title_indices
    ```
- How else can we determine the title? 
    - Assume the title starts on line 0.
    - Then: how do we determine whether the next non-empty line continues the title?
    - Files that don't start with a title on the first line:
        - Excluding ignored files, until I maybe fix them. There are 16 - 13 with the problem of no whitespace.
        - 9143, 9065, 8571 (arXiv version; has the watermark first)
            - Ok, only 3 cases. We can modify them.
    - Measure string similarity
        - If the next non-empty line _increases_ similarity upon the previous (combined) line, it's part of the title
        - It works well!
        - 8329 is suspicious: [0, 4, 5]
            - Ok, the main title is "Chasing Ghosts" and they pulled some fancy business by adding transparent copies of the title floating around. Manual edit? I could have a condition where if the current similarity is very close to previous, but it's such an edge case...
            - Actually wait a sec, this isn't even wrong! But what if the NER picks line 1, 2, or 3 as an entity? Then the rejection won't apply
            - **Manually edited 8329**

Next

- Consider non-standard symbols as clues
- Numbers at the start of names
    - Working example: 8323
    - I think it's because I'm using `match()` not `findall()`

`[^",}{\-\[\]\\&._\)/a-zA-Z\d\s:]`

Analysis

- For each affiliation, proportion of papers that released code
- For code and no-code, #occurrences of each affiliation (maybe multiple n-grams to group together variations on the same entity)

```
8646
Traceback (most recent call last):
  File "ner.py", line 223, in <module>
    main()
  File "ner.py", line 205, in main
    affiliations = extract_affiliations(txt_path, metadata, predictor)
  File "ner.py", line 122, in extract_affiliations
    header_lines = preprocess_header(header_lines)
  File "ner.py", line 54, in preprocess_header
    new_lines[i][match.start() - removed], '')
IndexError: string index out of range
```

## 2020.03.30

- Fixed index error
- 8646 is supplementary material

End results

- Wrote up script to compute proportion of code release per institute, and highest presence of institutes per code released or not
- I extracted affiliations by converting the paper PDFs to plain text and running a neural named entity tagger, along with some pre- and post-processing. I couldn't find a more convenient method, as affiliations are not given on the NeurIPS webpages. I initially tried extracting affiliations using a Google Scholar API, but that was slow and inaccurate.
- Current limitations
    - Does not capture several variables that may affect the decision to release code, such as commercial interests, theoretical vs. empirical work, ML vs. neuroscience, partial dependence on proprietary software.
    - The named entity tagger is good but imperfect, even with postprocessing. It occasionally mistakes author names or locations for organisations, includes extra bits outside the true entity, only detects part of the true entity. Or it completely misses a valid entity - I need to manually check several papers to get a sense of this.
    - Co-reference and hierarchy is currently not handled, e.g. unifying the same terms with slightly different spelling, or "Google" being a parent of "Google Research"
    - Missing 18 papers that had technical issues with processing
    - Missing 86 papers where the affiliation extraction algorithm returned nothing. I need to look into this, but at least one reason is affiliations listed at the bottom of the page (not detected) rather than above the abstract (detected).
- Some questions that came up while I was working on this:
    - How does the make-up of affiliations on a given paper, e.g. proportion of commercial affiliations, relate to code release?
    - Who is funding the research? Could scrape the acknowledgements section of papers to get information on this.
    - How often do reviewers point out or judge the presence or absence of code in their reviews?

Note: this project has taken about 18 hours so far.

## 2020.03.31

Papers that returned no affiliations

- Trying to get a sense of why, by checking at least a few samples
    ```
    ['8314', '8313', '9707', '9671', '9631', '9621', '9625', '9619', '9579', '9513', '9503', '9471', '9470', '9465', '9463', '9438', '9436', '9449', '9427', '9421', '9415', '9413', '9411', '9400', '9391', '9380', '9365', '9357', '9354', '9323', '9309', '9285', '9288', '9269', '9250', '9240', '9242', '9238', '9229', '9190', '9184', '9180', '9181', '9175', '9163', '9129', '9132', '9134', '9117', '9073', '9067', '9068', '9061', '9045', '9025', '9001', '9000', '8981', '8978', '8975', '8894', '8862', '8833', '8827', '8786', '8772', '8728', '8721', '8725', '8707', '8697', '8682', '8675', '8674', '8643', '8628', '8590', '8587', '8576', '8542', '8469', '8464', '8441', '8425', '8387', '8305']
    ```
    - 8314: page bottom
    - 8313: none; email only
    - 9707: page bottom
    - 9671: should have detected - UCLA, NYU
    - 9631: page bottom
    - 9621: page bottom
    - 9625: should have detected - DeepMind
    - 9619: page bottom
    - 9579: should have detected - DeepMind
    - 9513: page bottom
- Ok, so majority are page bottom, a significant amount are false negatives, and sometimes there's nothing there to begin with.
- When there's nothing, we could process the email address and do a lookup
- The false negatives may be systematic - DeepMind showed up twice.
    - Just searched DeepMind in the text data - 25 papers! And we only detected 2. This is a major failure; DeepMind is important.
- Side note: it seems that OpenAI does not publish at NeurIPS
- Oh, side note: I don't think we need the `passed_title` condition in postprocessing anymore, because we detect and ignore the title very reliably.
    - Removed it

- DeepMind failure
    - Checking 9625
    - It tags it as `U-PER`
    - Ok, so if we accept `U-PER`, I expect the false positive rate to go up. But those false positives will tend to be more specific to each paper, so they are unlikely to show up in top-N results of the analysis. Even if they do, a human can just realise what it is and ignore it.
    - I'm going to run debug on affiliation extraction with `U-PER` passed to get a sense of the detections
        - 'Shao' F (partial name)
        - 'LTCI' T
        - 'CMLA' T
        - 'Kligler' F (partial name)
        - 'zhangdinghuai' F (partial email)
        - 'Ming'
        - 'LTCI' T
        - 'Victorenko' F (partial name)
        - 'Institutskiy' F (partial location)
        - 'Abadeh' F (partial name)
        - 'Silva' F (partial name)
        - 'DeepMind' T
        - 'yshi' (partial name)
        - 'Stanford' T (partial institution)
        - 'Mila' T
        - 'Deepmind' T
        - 'Mila' T
        - 'Mila' T
        - 'Mila' T
        - 'ikajic' F (partial email)
    - Sometimes the partial names are rejected by the author matching, sometimes not
    - Usually the true positives are all-caps or camel-caps, but not always (e.g. Mila, Deepmind)
    - Ok, I think the best strategy is:
        - A hard-coded list: ['Mila', 'Deepmind', ...]
        - Plus regex: all-caps or camel-caps (where there must be at least one middle cap)
            - All caps: `'[A-Z][A-Z]+'`
            - Camel-caps: `'[A-Z]+[a-z]+[A-Z]+'` (doesn't necessarily match full string)

Effect of addressing false negatives

- Seems mostly improved overall
    - Biggest gains are DeepMind and Mila
- Some losses
    - "Technion Israel Institute of Technology2" -> "Israel Institute of Technology2" 2 (9008, 8831)
    - "Google" 1 (9086)
        - Tagged as 'O' (other)!
    - "Brain Team" 1 (9090) (all other cases preserved)
        - Tagged as 'O' (other)!
    - "Amazon AI" 1 (9406)
    - "UT Austin Amazon" -> nothing 1 (9538, 9542)
        - This is the one I was hoping would be fixed by keeping symbols space-separated, but it ended up returning nothing
        - Tagged as 'B-PER L-PER' and 'U-LOC'. Fair enough. Amazon is a location, Austin is a name.
    - 9572 lost 4/5 affiliations
- Reduced the net number of empty affiliations from 86 to 70

Detecting affiliations at page bottom

- 1413 of 1428 papers end the page with "33rd Conference" etc.
- 13 (disjoint) are the no-whitespace cases with "33rdConference" etc.
- The 2 exceptions are probably the ones encoded as images, which are ignored anyway.
- Ok that's one great signal. What about where to stop, when you go bottom-up?
- Regex: symbol followed by alphanumeric
    - `^([^\x00-\x7F]|[0-9])[A-Za-z]+`
    - Start of line, then either a non-ascii character or a number, then letters
    - I've seen a pattern more or less like this for 4 files:
        ```
        1Department of Engineering, University of Cambridge, Cambridge, UK
        ∗Contributed during internship in Microsoft Research
        2Microsoft Research, Cambridge, UK
        †Now at Google AI, Berlin, Germany (contributed while being with Microsoft Research)

        Correspondence to: Cheng Zhang <Cheng.Zhang@microsoft.com> and Wenbo Gong <wg242@cam.ac.uk>

        33rd Conference on Neural Information Processing Systems (NeurIPS 2019), Vancouver, Canada.
        ```
    - How to process?
        - Enumerate lines
        - When '33rd Conference' is matched store line index for that
        - Enumerate lines in reverse from that line
        - Skip until first match to regex above
        - Add lines until the regex is not matched, then break
- Remaining failures
    - Universities with non-English spelling (model is probably biased towards English), tend to get tagged as person or location
    - Ideosyncratic cases, e.g. Amazon as location
        - We should probably just have it as a special exception; it occurs a lot
    - By including Amazon we are now down to 30 complete failures

Removing trailing numbers from already-tagged entities

- Worked like a charm. The only casualty was Data61, but that is still recogniseable as Data6
- There are some cases where multiple entities are caught in one, so there is still a trailing number internally. But it's difficult to separate that from the legitimate case of, say, Web3 Foundation, which occurs twice.


