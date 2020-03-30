import json
import scholarly
import pickle


def get_affiliation(author_name, pub_title):
    # Retrieve the author's data
    search_query = scholarly.search_author(author_name)
    # Iterate over authors until we find a likely match
    i = 0
    while i < 5:
        try:
            author = next(search_query)
        except:
            return None
        # Fill in their profile information
        author = author.fill()
        # Get the titles of their publications
        pub_titles = {pub.bib['title'] for pub in author.publications}
        pub_titles = {title.lower() for title in pub_titles}
        # Did they publish this one?
        if pub_title.lower() in pub_titles:
            break
        i += 1
    if i >= 5:
        return None
    else:
        return author.affiliation


def get_pub_info(pub):
    title = pub['title']
    authors = pub['authors']
    print('\nTitle:', title)
    affs = list()
    for author in authors:
        aff = get_affiliation(author, title)
        affs.append(aff)
        print(f'{author} ({aff})')
    return title, authors, affs


def main():
    fname = './out/neurips_2019/papers_metadata.json'
    with open(fname, 'r') as f:
        data = json.load(f)
    
    pubs_with_code = list()
    pubs_without_code = list()
    for pub in data:
        code = pub['code']
        if code:
            pubs_with_code.append(pub)
        else:
            pubs_without_code.append(pub)

    print('\nNeurIPS 2019')
    
    print('\n=============================================')
    print('Publications that did not release source code')
    print('=============================================')
    affs_without_code = list()
    for pub in pubs_without_code:
        title, authors, affs = get_pub_info(pub)
        affs_without_code.append(affs)
    
    print('\n======================================')
    print('Publications that released source code')
    print('======================================')
    affs_with_code = list()
    for pub in pubs_with_code:
        get_pub_info(pub)
        affs_with_code.append(affs)

    all_affs = {'code': affs_with_code, 'no-code': affs_without_code}
    with open('affiliations.pkl', 'wb') as f:
        pickle.dump(all_affs, f)
    

if __name__ == '__main__':
    main()
