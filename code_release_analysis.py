import json
from collections import defaultdict
import argparse


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


def frequency_per_code_release(data, words=False,
    ignore=['department', 'school']):
    code_freq = defaultdict(int)
    no_code_freq = defaultdict(int)
    for item in data:
        code_released = item['code']
        freq = code_freq if code_released else no_code_freq
        affiliations = item['affiliations']
        # Remove duplicates
        affiliations = set(affiliations)
        for aff in affiliations:
            if any([(ig in aff.lower()) for ig in ignore]):
                continue
            if words:
                for word in aff.split(' '):
                    freq[word] += 1
            else:
                freq[aff] += 1
    return code_freq, no_code_freq


def rank_frequency_per_code_release(data, top=10):
    code_freq, no_code_freq = frequency_per_code_release(data)
    print("\nPapers with code\n")
    print_ranked_freq(code_freq, top=top)
    print("\nPapers without code\n")
    print_ranked_freq(no_code_freq, top=top)


def rank_code_release_frequency_per_entity(data, top=10, min_count=0):
    code_freq, no_code_freq = frequency_per_code_release(data)
    rel_freq = defaultdict(tuple)
    for k, v in code_freq.items():
        v2 = no_code_freq[k]
        v_tot = v + v2
        if v_tot > min_count:
            rel_freq[k] = (round(v / (v_tot), 2), v_tot)
    # sort_key = lambda i: i[1][0]
    print("\nLowest fraction of papers with code\n")
    print_ranked_freq(rel_freq, top=top, reverse=False)
    print("\nHighest fraction of papers with code\n")
    print_ranked_freq(rel_freq, top=top, reverse=True)


def main(args):
    with open(args.input, 'r') as f:
        data = json.load(f)

    print('======================')
    print('Code release fraction')
    print('======================\n')
    print('Format: rank. name (fraction, #papers)')

    print('\nAll institutions')
    print('================')
    rank_code_release_frequency_per_entity(data, top=10, min_count=1)
    print('\nInstitutions with at least 10 papers')
    print('====================================')
    rank_code_release_frequency_per_entity(data, top=10, min_count=10)

    print('\n============================')
    print('Most papers per code release')
    print('============================\n')
    print('Format: rank. name #papers')
    
    rank_frequency_per_code_release(data, top=10)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, 
                        default='./out/neurips_2019/affiliations.json',
                        help='Path to affiliation JSON data')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
