import json
from collections import defaultdict
import argparse


IGNORE_PART = ['department', 'school']
IGNORE_FULL = ['AI', 'arXiv']
STOPWORDS = [
    'the', 'de', ',', 
    'artificial', 'intelligence', 'automation'
]


def print_ranked_freq(freq, top=10, reverse=True, sort_key=None):
    if sort_key is None:
        sort_key = lambda i: i[1]
    i = 0
    for k, v in sorted(freq.items(), 
        key=sort_key, reverse=reverse):
        print(f'{i+1}. {k} {v}')
        i += 1
        if i >= top:
            break


def frequency_per_code_release(data, words=False):
    code_freq = defaultdict(int)
    no_code_freq = defaultdict(int)
    for item in data:
        code_released = item['code']
        freq = code_freq if code_released else no_code_freq
        affiliations = item['affiliations']
        affiliations = [aff for aff in affiliations if not (
            any([(ig in aff.lower()) for ig in IGNORE_PART]) or 
            any([aff == ig for ig in IGNORE_FULL]))]
        if words:
            aff_words = set((' '.join(affiliations)).split(' '))
            for word in aff_words:
                if any([word.lower() == sw for sw in STOPWORDS]):
                    continue
                freq[word] += 1
        else:
            # Remove duplicates
            affiliations = set(affiliations)
            for aff in affiliations:
                freq[aff] += 1
    return code_freq, no_code_freq


def rank_frequency_per_code_release(data, top=10, **kwargs):
    code_freq, no_code_freq = frequency_per_code_release(data, **kwargs)
    print("\nPapers with code\n")
    print_ranked_freq(code_freq, top=top)
    print("\nPapers without code\n")
    print_ranked_freq(no_code_freq, top=top)


def compute_relative_code_release_frequency(code_freq, no_code_freq, min_count=0):
    rel_freq = defaultdict(tuple)
    for k, v in code_freq.items():
        v2 = no_code_freq[k]
        v_tot = v + v2
        if v_tot > min_count:
            rel_freq[k] = (round(v / (v_tot), 2), v_tot)
    return rel_freq


def rank_code_release_frequency_per_entity(data, top=10, min_count=0, 
        print_all=False, **kwargs):
    code_freq, no_code_freq = frequency_per_code_release(data, **kwargs)
    rel_freq = compute_relative_code_release_frequency(code_freq, no_code_freq, min_count)
    if print_all:
        print_ranked_freq(rel_freq, top=len(rel_freq))
    else:
        print("\nLowest fraction of papers with code\n")
        sort_key_low = lambda k: (k[1][0], -k[1][1])
        print_ranked_freq(rel_freq, top=top, reverse=False, sort_key=sort_key_low)
        print("\nHighest fraction of papers with code\n")
        print_ranked_freq(rel_freq, top=top, reverse=True)


def rank_pubs_per_code_release(data, top=10, min_count=0, **kwargs):
    code_freq, no_code_freq = frequency_per_code_release(data, **kwargs)
    rel_freq = compute_relative_code_release_frequency(code_freq, no_code_freq, min_count)
    sort_key = lambda i: i[1][1]
    print("\nCode release fraction for biggest publishers\n")
    print_ranked_freq(rel_freq, top=top, reverse=True, sort_key=sort_key)


def main(args):
    with open(args.input, 'r') as f:
        data = json.load(f)
        
    if args.full:
        # Full list
        rank_code_release_frequency_per_entity(data, print_all=True)
        return

    print('======================')
    print('Code release fraction')
    print('======================\n')
    print('Format: rank. name (fraction, #papers)')

    print('\nInstitutions')
    print('============')
    rank_code_release_frequency_per_entity(data, top=20, min_count=1)

    print('\nWords (#papers >= 5)')
    print('=====')
    rank_code_release_frequency_per_entity(data, top=20, min_count=5, words=True)

    print('\nBiggest publishers')
    print('==================')
    rank_pubs_per_code_release(data, top=20)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, 
                        default='./out/neurips_2019/affiliations.json',
                        help='Path to affiliation JSON data')
    parser.add_argument('-f', '--full', action='store_true',
                        help='Report full list of affiliations')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
