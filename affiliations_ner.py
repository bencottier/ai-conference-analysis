import spacy
from nltk.metrics.distance import edit_distance
from string_sim import cos_sim_pair
from allennlp import pretrained
import re
import json
from pprint import pprint
import os
import argparse


UNICODE_CONVERSION = {
    '\u0133': 'ij',
    '\ufb00': 'ff',
    '\ufb01': 'fi',
    '\ufb02': 'fl',
    '\ufb03': 'ffi',
    '\ufb04': 'ffl',
}


def is_valid_line(line, index=None, invalid_indices=list()):
    if len(line) < 1:
        return False
    elif len(invalid_indices) > 0 and index in invalid_indices:
        return False
    return True


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
            # NOTE assumption: affiliations listed above abstract
            if 'Abstract\n' in line:
                break
            else:
                line = line.strip()
                if is_valid_line(line):
                    header_lines.append(line)
            i += 1
    
    # pprint(header_lines)
    header_lines = preprocess_header(header_lines)
    # print("")
    # pprint(header_lines)

    title_indices = find_title(header_lines, metadata['title'])
    # print(title_indices)

    results = []
    for i, line in enumerate(header_lines):
        if not is_valid_line(line, index=i, invalid_indices=title_indices):
            continue
        result = predictor.predict(sentence=line)
        # for word, tag in zip(result["words"], result["tags"]):
        #     print(f"({tag}) {word}", end=" ")
        # print("")
        results.append(result)
    
    affiliations = postprocess_entities(results, metadata)
    pprint(affiliations)

    return affiliations


def find_title(header_lines, title):
    title_indices = list()
    title_started = False
    cum_sim = 0.0
    cum_line = str()
    title_ = title.strip().lower()
    for i, line in enumerate(header_lines):
        line_ = line.strip().lower()
        sim = cos_sim_pair(title_, line_)
        if not title_started and sim > 0.2:
            title_started = True
            cum_sim = sim
            cum_line = line_
            title_indices.append(i)
        elif title_started:
            combined = ' '.join([cum_line, line_])
            combined_sim = cos_sim_pair(title_, combined)
            if combined_sim > cum_sim:
                # Similarity increased by appending this line
                # Therefore, likely continuation of title
                cum_sim = combined_sim
                cum_line = combined
                title_indices.append(i)
    assert len(title_indices) != 0
    return title_indices


def write_output(fname, output):
    with open(fname, 'w') as f:
        json.dump(output, f, indent=4)


def main(args):
    fname = args.metadata
    with open(fname, 'r') as f:
        metadatas = json.load(f)

    print('Building model...')
    predictor = pretrained.named_entity_recognition_with_elmo_peters_2018()
    
    # Ignore problematic files
    ignore = [
        '9724',  # PDF not available on website
        '9659', '9165', '8511', '9485', '9430', '9393', '9341', '9245', 
        '9166', '8858', '8687', '8574', '8518',  # no whitespace
        '9305', '9171',  # Each page is an image
        '8823',  # NeurIPS template PDF (probably mistaken)
        '8646',  # Supplementary material (probably mistaken)
    ]

    output = list()
    data_path = args.data

    for i, metadata in enumerate(metadatas):
        pdf_fname = os.path.split(metadata['pdf'])[1]
        if any([ig in pdf_fname for ig in ignore]):
            continue
        txt_fname = pdf_fname.replace('.pdf', '.txt')
        txt_path = os.path.join(data_path, txt_fname)
        paper_id = pdf_fname.split('-')[0]
        print(paper_id)

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
            write_output(args.output, output)

    write_output(args.output, output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metadata', type=str, 
                        default='./out/neurips_2019/papers_metadata.json',
                        help='Path to metadata JSON file with PDF URLs')
    parser.add_argument('-d', '--data', type=str, 
                        default='./data/neurips_2019/txt',
                        help='Folder containing papers in text format')
    parser.add_argument('-o', '--output', type=str, 
                        default='./out/neurips_2019/affiliations.json', 
                        help='File to write affiliation data')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
