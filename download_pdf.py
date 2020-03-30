import urllib.request
import json
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metadata', type=str, 
                        default='./out/neurips_2019/papers_metadata.json',
                        help='Path to metadata JSON file with PDF URLs')
    parser.add_argument('-o', '--output', type=str, 
                        default='./data/neurips_2019/pdf', 
                        help='Folder to save PDFs in')
    return parser.parse_args()


def main(args):
    fname = args.metadata
    with open(fname, 'r') as f:
        data = json.load(f)

    os.makedirs(args.output, exist_ok=True)
    
    for item in data:
        download_file(item['pdf'], args.output)


def download_file(download_url, output):
    fname = os.path.split(download_url)[1]
    try:
        response = urllib.request.urlopen(download_url)
    except urllib.request.HTTPError as e:
        print(f"Failed to write {fname}:")
        print(e)
        return
    f = open(os.path.join(output, fname), 'wb')
    f.write(response.read())
    f.close()
    print("Wrote", fname)


if __name__ == "__main__":
    args = parse_args()
    main(args)
