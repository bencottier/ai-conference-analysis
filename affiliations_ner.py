import spacy
from nltk.metrics.distance import edit_distance
from allennlp import pretrained
import re
import json
from pprint import pprint
import os


UNICODE_CONVERSION = {
    '\u0133': 'ij',
    '\ufb00': 'ff',
    '\ufb01': 'fi',
    '\ufb02': 'fl',
    '\ufb03': 'ffi',
    '\ufb04': 'ffl',
}


def preprocess_header(lines):
    new_lines = lines
    # Remove symbols
    for i, line in enumerate(new_lines):
        for char in line:
            if UNICODE_CONVERSION.get(char) is not None:
                new_lines[i] = new_lines[i].replace(char, 
                    UNICODE_CONVERSION[char])
            elif not (char.isalnum() or char.isascii()):
                new_lines[i] = new_lines[i].replace(char, '')
    # Remove numbers at the start of words (footnotes)
    for i, line in enumerate(new_lines):
        number_pattern = re.compile('[0-9][A-Za-z]')
        removed = 0
        for match in re.finditer(number_pattern, line):
            new_line = new_lines[i]
            new_line = new_line[:match.start() - removed] + \
                new_line[match.start() - removed + 1:]
            removed += 1
            new_lines[i] = new_line
    # Strip lines in case only whitespace remains
    new_lines = [line.strip() for line in new_lines]
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
    # Check if entity is an email address
    if '@' in entity and '.' in entity:
        return False
    # Check if entity is actually a person (author from metadata)
    for author in metadata['authors']:
        dist = edit_distance(clean_entity, author)
        if (dist / len(author)) < threshold:
            # Close enough to be an author, therefore not affiliation
            return False
    # Ignore university schools and departments
    # NOTE this is imperfect: there is 'college', 'laboratory', etc.
    # if any([x in entity.lower() for x in ['school', 'department']]):
    #     return False
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

    print('Building model...')
    predictor = pretrained.named_entity_recognition_with_elmo_peters_2018()

    output = list()
    base_path = './data/neurips_2019/txt'
    ignore = ['9724'] # PDF not found
    for i, metadata in enumerate(metadatas):
        pdf_fname = os.path.split(metadata['pdf'])[1]
        if any([ig in pdf_fname for ig in ignore]):
            continue
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
