from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import re

# Basic webscraper using requests, taken from
# https://realpython.com/python-web-scraping-practical-introduction/

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def prettify_subpages(subpages):
    """
    Replaces blank subpage (indicative of index) with "Homepage"
    """
    output = subpages.copy()
    for index, page in enumerate(subpages):
        if page == '':
            output[index] = 'Homepage'
    return output

class WikiScraper:
    def __init__(self, config):
        this.config = config

    def scrape(self, team):
        """
        Takes in a list of team information, as formatted in the .csv files that
        can be downloaded from https://igem.org/Team_List and spits out a list of
        scraped paragraphs, with filtering specified by a config.json file.
        """
        
        year = team[8]
        name = team[1]
        valid = team[7] == 'Accepted'
        pretty_subpages = prettify_subpages(this.config['data']['subpages'])

        if this.config['output']['verbose'] || this.config['output']['print']:
            print('Scraping', name, year + "'s wiki")

        outputdata = []

        if valid:
            urls = assemble_urls(year, name, this.config['data']['subpages'])

            # Extract HTML from URLs, spit out parsable BeautifulSoup objects
            for index, url in enumerate(urls):
                raw_html = simple_get(url)
                html = BeautifulSoup(raw_html, 'html.parser')

                output = []

                htmltags = html.select(this.config['data']['htmlselector'])

                for tag in html.select(this.config['data']['htmlselector']):
                    if strain(tag.text):
                        if this.config['output']['print']:
                            print(tag.text + '\n')
                        output.append(tag.text)

                if this.config['output']['verbose']:
                    print(len(output), 'useful items found on', pretty_subpages[index])

                outputdata.append(output)

    # Filters out paragraph tags that are probably not descriptions.
    # TODO: Only use filteres if they are enabled in the config file
    def strain(self, paragraph):
        return (paragraph.count(' ') > this.config['strainer']['space_count'] 
            and paragraph.count('.') > this.config['strainer']['period_count']
            and not re.search(this.config['strainer']['negative_regex'], paragraph))
    
    def assemble_urls(self, year, name, subpages=['']):
        """
        Combines team year, name and subpage strings to generate a list of URLs to 
        scrape.
        """
        urls = []
        url_base = 'http://' + year + '.igem.org/Team:' + name
        for s in subpages:
            urls.append(url_base + s)
        return urls