import urllib.request
import json
import os


PDF_PATH = './data/neurips_2019/pdf'


def main():
    fname = './code_stat.json'
    with open(fname, 'r') as f:
        data = json.load(f)
    
    for item in data:
        download_file(item['pdf'])


def download_file(download_url):
    fname = os.path.split(download_url)[1]
    try:
        response = urllib.request.urlopen(download_url)
    except urllib.request.HTTPError as e:
        print(f"Failed to write {fname}:")
        print(e)
        return
    f = open(os.path.join(PDF_PATH, fname), 'wb')
    f.write(response.read())
    f.close()
    print("Wrote", fname)


if __name__ == "__main__":
    main()
