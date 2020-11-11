import requests
import argparse
from bs4 import BeautifulSoup
import pandas as pd


def extract(url):
    name = "contents_page"
    r = requests.get(url)
    contents = r.text
    with open(name, 'w') as fh:
        fh.write(contents)
    soup = BeautifulSoup(contents, 'html.parser')

    return soup

def scrape_info(soup):

    class_name = soup.find_all('h4', 'field-content')
    ls = [i.find('a').text for i in class_name]

    list_ID = []
    list_name = []
    list_credit = []
    for class_info in ls:
        splitted_class = class_info.split(" ", 2)
        courseID = splitted_class[0] + " " + splitted_class[1]
        list_ID.append(courseID)
        courseName = splitted_class[2].split(" (")
        list_name.append(courseName[0])
        credit = courseName[1].split(" ")
        credit_splitted = credit[0]
        list_credit.append(credit_splitted)

    data = {'Course ID': list_ID,
            'Course Name': list_name,
            '# of credits': list_credit}

    df = pd.DataFrame(data, columns= ['Course ID', 'Course Name', '# of credits'])

    return df


def main():
    parser = argparse.ArgumentParser(description='Reading and writing JSON files')
    parser.add_argument('-c', '--input_file', help='path to config file')
    parser.add_argument('page_number', help='page_number specified')

    args = parser.parse_args()
    input = args.input_file

    x = args.page_number
    url = str("https://www.mcgill.ca/study/2020-2021/courses/search?page=" + x)

    df = scrape_info(extract(url))

    df.to_csv(str(args.input_file + args.page_number + '.csv'), index = False)


if __name__ == '__main__':
    main()