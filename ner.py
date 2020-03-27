import spacy
from nltk.metrics.distance import edit_distance
from allennlp import pretrained
import re
import json
from pprint import pprint
import os


# EN_MODEL = spacy.load('en_core_web_sm')
# PATH = './data/neurips_2019/txt/8317-imitation-learning-from-observations-by-minimizing-inverse-dynamics-disagreement.txt'
# PATH = 'data/neurips_2019/txt/9668-robust-exploration-in-linear-quadratic-reinforcement-learning.txt'
# PATH = 'data/neurips_2019/txt/9715-generalization-in-multitask-deep-neural-classifiers-a-statistical-physics-approach.txt'
# PATH = 'data/neurips_2019/txt/9721-re-randomized-densification-for-one-permutation-hashing-and-bin-wise-consistent-weighted-sampling.txt'
# PATH = 'data/neurips_2019/txt/9723-mixtape-breaking-the-softmax-bottleneck-efficiently.txt'
# PATH = 'data/neurips_2019/txt/9704-on-the-transfer-of-inductive-bias-from-simulation-to-the-real-world-a-new-disentanglement-dataset.txt'


def preprocess_header(lines):
    new_lines = lines
    # Remove symbols
    for i, line in enumerate(new_lines):
        for char in line:
            if not (char.isalnum() or char.isascii()):
                new_lines[i] = new_lines[i].replace(char, '')
    # Remove numbers at the start of words (footnotes)
    for i, line in enumerate(new_lines):
        number_pattern = re.compile('[0-9] ?[A-Za-z]')
        match = re.match(number_pattern, line)
        if match:
            new_lines[i] = line.replace(line[match.start()], '')
    return new_lines


def postprocess_entities(results, metadata):
    entities = list()

    def maybe_add_entity(entity):
        if is_valid_entity(entity, metadata):
            entities.append(entity)

    passed_title = False
    for result in results:
        entity = str()
        for i, (word, tag) in enumerate(zip(result["words"], result["tags"])):
            if 'PER' in tag or (i == 0 and 'ORG' in tag):
                # Not a perfect indication, but gets the vast majority
                passed_title = True
            if not passed_title:
                continue
            elif tag == 'U-ORG':
                maybe_add_entity(word)
            elif tag == 'B-ORG':
                entity += word
            elif tag == 'I-ORG':
                entity += ' ' + word
            elif tag == 'L-ORG':
                entity += ' ' + word
                maybe_add_entity(entity)
                entity = str()
    return entities


def is_valid_entity(entity, metadata, threshold=0.25):
    clean_entity = ''.join(c for c in entity if not c.isdigit())
    # Check if entity is actually a person (author from metadata)
    for author in metadata['authors']:
        dist = edit_distance(clean_entity, author)
        if (dist / len(author)) < threshold:
            # Close enough to be an author, therefore not affiliation
            return False
    if any([x in entity.lower() for x in ['school', 'department']]):
        # Don't care about university schools and departments
        return False
    return True


def extract_affiliations(txt_path, metadata, predictor):
    with open(txt_path, 'r') as f:
        i = 0
        header_lines = list()
        for line in f.readlines():
            if 'Abstract' in line:
                break
            else:
                header_lines.append(line.strip())
            i += 1
    
    pprint(header_lines)
    header_lines = preprocess_header(header_lines)
    print("")
    pprint(header_lines)

    results = []
    for line in header_lines:
        if len(line) < 1:
            continue
        result = predictor.predict(sentence=line)
        for word, tag in zip(result["words"], result["tags"]):
            print(f"({tag}) {word}", end=" ")
        print("")
        results.append(result)
    
    affiliations = postprocess_entities(results, metadata)
    pprint(affiliations)

    return affiliations


def write_output(output):
    with open('./out/affiliations.json', 'w') as f:
        json.dump(output, f, indent=4)


def main():
    fname = './out/code_stat.json'
    with open(fname, 'r') as f:
        metadatas = json.load(f)

    predictor = pretrained.named_entity_recognition_with_elmo_peters_2018()

    output = list()
    base_path = './data/neurips_2019/txt'
    for i, metadata in enumerate(metadatas):
        pdf_fname = os.path.split(metadata['pdf'])[1]
        txt_fname = pdf_fname.replace('.pdf', '.txt')
        txt_path = os.path.join(base_path, txt_fname)
        affiliations = extract_affiliations(txt_path, metadata, predictor)
        has_code = metadata['code']
        data = {
            'name': pdf_fname.replace('.pdf', ''),
            'code': has_code,
            'affiliations': affiliations
        }
        output.append(data)
        if i % 100 == 0:
            # Write periodically as a failsafe
            write_output(output)
    write_output(output)


if __name__ == '__main__':
    main()
