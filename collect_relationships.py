import json
import argparse
import os.path as osp
from bs4 import BeautifulSoup
import hashlib
import requests


def extract_relationships_from_candidate_links(candidates, person_url):
    relationships = []
    for link in candidates:
        if 'href' not in link.attrs:
            print(f'skipping {link}')
            continue
        href = link['href']

        if href.startswith('/dating') and href != str('/dating/') + person_url:
            relationships.append(href)

    return relationships


def extract_relationships(person_url, soup):
    """
    extract all the relationships in the file... which should've been downloaded from whosdatingwho.com
    """
    relationships = []

    # get current relationship
    # grab the h4 with class = ff-auto-status

    status_h4 = soup.find('h4', 'ff-auto-status')

    # grab the next sibling
    key_div = status_h4.next_sibling

    # grab all the a elements
    candidate_links = key_div.find_all('a')

    relationships.extend(extract_relationships_from_candidate_links(candidate_links, person_url))

    if len(relationships) > 1:
        raise Exception('Too many relationships - should have only one')

    # get all prior relationships
    rels_h4 = soup.find('h4', 'ff-auto-relationships')
    sib = rels_h4.next_sibling

    while sib is not None and sib.name == 'p':
        candidate_links = sib.find_all('a')
        sib = sib.next_sibling

        relationships.extend(extract_relationships_from_candidate_links(candidate_links, person_url))

    return relationships


def get_url_content(cache_dir, target_person):
    url = str("https://www.whosdatedwho.com/dating/" + target_person)

    fname = hashlib.sha1(url.encode('utf-8')).hexdigest()

    full_fname = osp.join(cache_dir, fname)

    contents = None
    if osp.exists(full_fname):
        soup = BeautifulSoup(open(full_fname, 'r'), 'html.parser')
    else:
        r = requests.get(url)
        contents = r.text
        with open(full_fname, 'w') as fh:
            fh.write(contents)
        soup = BeautifulSoup(contents, 'html.parser')

    return soup


def read_file(input):
    posts = {}
    i = 0
    with open(input) as f:
        data = json.load(f)
    return data


def main():
    parser = argparse.ArgumentParser(description='Reading and writing JSON files')
    parser.add_argument('-c', '--input_file', help='path to config file')
    parser.add_argument('-o', '--output_file', help='output file, in JSON format')

    args = parser.parse_args()
    input = args.input_file
    output = args.output_file

    data = read_file(input)

    output_dict = {}

    for person in data["target_people"]:

        soup = get_url_content(data["cache_dir"], person)
        output_dict[person] = extract_relationships(person, soup)


    with open(output, 'w') as f:
        json.dump(output_dict, f)
        f.write('\n')

if __name__ == '__main__':
    main()
