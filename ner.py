import spacy
from spacy import displacy
from collections import Counter
from pprint import pprint


EN_MODEL = spacy.load('en_core_web_sm')
PATH = './data/neurips_2019/txt/8317-imitation-learning-from-observations-by-minimizing-inverse-dynamics-disagreement.txt'
# PATH = 'data/neurips_2019/txt/9668-robust-exploration-in-linear-quadratic-reinforcement-learning.txt'

def main():
    with open(PATH, 'r') as f:
        i = 0
        header_lines = list()
        for line in f.readlines():
            if 'Abstract' in line:
                break
            else:
                header_lines.append(line)
            i += 1
    header = ''.join(header_lines)
    header = header.replace('\n', ' ')
    print(header)
    doc = EN_MODEL(header)
    pprint([(ent.text, ent.label_) for ent in doc.ents])

    filtered_ents = list()
    for ent in doc.ents:
        if ent.label_ not in ['ORG', 'PERSON']:
            continue
        if not ent.text[0].isupper():
            continue
        if any([x in ent.text.lower() for x in ['school', 'lab', 'department']]):
            continue
        filtered_ents.append(ent)
    pprint([(ent.text, ent.label_) for ent in filtered_ents])


if __name__ == '__main__':
    main()
