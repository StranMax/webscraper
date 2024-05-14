"""
Python script for Querying OAI-PMH Services.

Developed specifically for need to download large amounts of pdf documents
from Finnish Kansallisarkisto.

This program requires following packages (test phase):
  - sickle 0.7.0  (OAI-PMH)
"""

__author__ = "Max Strandén"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import logging
import xml.etree.ElementTree as ET
import pprint
import re
import requests
import urllib

from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from lxml import etree
from pathlib import Path
from urllib.parse import urlparse, unquote, quote

from sickle import Sickle
from sickle.iterator import OAIResponseIterator


class KansallisarkistoOAI():
    # All the sets are here: https://julkaisut.valtioneuvosto.fi/oai/request?verb=ListSets
    sets_lookup = {
    "Valtioneuvoston kanslia": 'com_123456789_1',
    "Ulkoministeriö": 'com_123456789_59333',
    "Oikeusministeriö": 'com_10024_59349',
    "Sisäministeriö": 'com_10024_59351',
    "Puolustusministeriö": 'com_10024_59353',
    "Valtiovarainministeri": 'com_10024_59355',
    "Opetus- ja kulttuuriministeriö": 'com_10024_59357',
    "Maa- ja metsätalousministeriö": 'com_10024_59359',
    "Liikenne- ja viestintäministeriö": 'com_10024_59361',
    "Työ- ja elinkeinoministeriö": 'com_10024_59367',
    "Sosiaali- ja terveysministeriö": 'com_10024_59365',
    "Ympäristöministeriö": 'com_10024_59367',
    "Valtioneuvosto": 'com_10024_161139',
    "Muut toimijat": 'com_10024_162645',
    }
    metadata = 'kk'

class Record():
    counter = 0
    idx = 0
    def __init__(self, response):
        Record.idx += 1
        self.title = None
        self.abstract = None
        self.publication = None
        self.publisher = None
        self.key_words = []
        self.language = None
        self.published = None
        self.urls = []
        self.xml = response.xml
        self._parse_metadata()
        
    def _parse_metadata(self):
        for field in self.xml.findall(".//{http://kk/1.0}field"):
            elem = field.get("element")
            qualif = field.get("qualifier")
            value = field.get("value")
            
            match (elem, qualif):
                case ("title", None):
                    self.title = value
                case ("description", "abstract"):
                    self.abstract = value
                case ("relation", "ispartofseries"):
                    self.publication = value
                case ("publisher", None):
                    self.publisher = value
                case ("subject", None):
                    self.key_words.append(value)
                case ("language", "iso"):
                    self.language = value
                case ("date", "issued"):
                    self.published = value
        
        for file in self.xml.findall(".//{http://kk/1.0}file"):
            type = file.get("type")
            href = file.get("href")
            if type=="application/pdf":
                    self.urls.append(href)
    
    def __repr__(self):
        return f'Record({response})'
    
    def __str__(self):
        return f"{self.title} ({self.published}). {self.publication}, {self.publisher}"
        
    def _match(self, pattern):    
        entries = [i for i in [self.title, 
                               self.abstract, 
                               *self.key_words]
                   if i is not None
                  ]
        if not pattern:
            return True
        else:
            matches = [re.search(pattern, entry) for entry in entries]
            return any(matches)
            
        
    def _check_language(self, language):
        if not language:
            return True
        else:
            return self.language == language
            
        
    def filter(self, language, pattern):
        #logging.info("Checking record: %s", self.title)
        if self._check_language(language) and self._match(pattern):
            Record.counter += 1
            logging.info("Record no. %s: %s", Record.idx, self.title)
            return True
        else:
            logging.debug("Skip record no. %s: %s", Record.idx, self.title)
            return False


class Records(KansallisarkistoOAI):
    default_params = {'metadataPrefix': 'kk' , 
                      'ignore_deleted': True}
                      
    # Initialize with all records
    def __init__(self, endpoint, sets):
        logging.info("Connected to: %s", endpoint)
        self.oai_service = Sickle(endpoint)
        #self.params = []
        self.records = []
        self.idx = 0
        self.sets = sets
        self.list_records()
        
    # Helper function for list_records
    def _create_param_sets(self):
        if self.sets is not None:           
            return [{**Records.default_params, 'set': self.sets_lookup[set]} for set in self.sets]
        else:
            return [{**Records.default_params}]
    
    # Initializer for records
    def list_records(self):
        for param_set in self._create_param_sets():
            self.records.append(self.oai_service.ListRecords(**param_set))
    
    # Custom iterator
    def __iter__(self):
        return self
        
    # Transform each item to Record class
    def __next__(self):
        for records in self.records:
            record = records.next()
            if record is not None:
                self.idx += 1
                return Record(record)
            else:
                raise StopIteration

class Downloader():
    #urls = []
    
    def __init__(self, outdir):
        self._outdir = outdir
        self._urls = []
        self._download_attempt = 0
        self._download_success = 0
        
    @property
    def outdir(self):
        return self._outdir
        
            
    @outdir.setter
    def outdir(self, value):
        if value is not None:
            self._outdir = Path(value)
        else:
            self._outdir = Path('.')
    
    @property
    def url(self):
        return self._urls
        
    @url.setter
    def url(self, value):
        logging.debug("Appending %s to downloader", value)
        self._urls.append(value)
        self._download_attempt += 1
        logging.debug("Downloader has %s urls", len(self._urls))
        if len(self._urls) == 1000:
            logging.info("Stored urls reached %s", len(self._urls))
            self.threaded_download()
            del self.url
            
    @url.deleter
    def url(self):
        logging.info("Deleting %s urls from downloader", str(len(self._urls)))
        self._urls.clear()
    
    def download_file(self, url):
        try:
            response = requests.get(url, allow_redirects=True)
        except UnicodeError:
            logging.warning("Problem with url: %s", url)
            resolved_url = urllib.request.urlopen(url).geturl()
            logging.warning('Trying fixed url: %s', resolved_url)
            response = requests.get(resolved_url, allow_redirects=True)
        if "content-disposition" in response.headers:
            content_disposition = response.headers["content-disposition"]
            filename = content_disposition.split("filename=")[1]
        else:
            filename = url.split("/")[-1]
        with open(self._outdir / Path(filename), mode="wb") as file:
            file.write(response.content)
            self._download_success += 1
            logging.info('Downloaded file: %s', filename)
        
    def threaded_download(self):
        logging.debug("Starting threaded download with %s files", len(self._urls))
        with ThreadPoolExecutor() as executor:
            executor.map(self.download_file, self._urls)
        logging.debug("Finished threaded download")
        logging.debug('Currently %s attempted downloads and %s succesfully downloaded', self._download_attempt, self._download_success)
    
def cli_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("URL", 
                        metavar="<oai-pmh-service-url>",
                        help=("OAI-PMH service, for example: "
                        'https://julkaisut.valtioneuvosto.fi/oai/request'), 
                        type=str)

    parser.add_argument("-lim", "--limit", 
                        metavar="<integer>",
                        help="Number of records to limit query",
                        type=int, default=None)

    parser.add_argument("-p", "--publishers", 
                        choices=list(KansallisarkistoOAI.sets_lookup.keys()), metavar="'Ympäristöministeriö|Valtioneuvosto|...'",
                        help="""Limit search for certain publishers. Defaults to all. Use -lp to list publishers.""",
                        type=str, nargs='*', default=None)
                        
    parser.add_argument("-l", "--language", 
                        choices=['fi', 'sv', 'en'],
                        help="Limit to specific language",
                        type=str, default=None)
    
    parser.add_argument("-lp", "--listpublishers",
                        help="List available sets/publishers",
                        action="store_true")
    
    parser.add_argument("-sp", "--searchpattern",
                        help="Filter documents by regex",
                        type=str, default=None)
                        
    parser.add_argument("-o", "--outdir",
                        type=str,
                        help="download files to location")
                        
    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity of metadata printing (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    return parser.parse_args()
    
def main():
    """ Main entry point of the app """
    args = cli_args()
    # Command line arguments
    LISTPUBLISHERS = args.listpublishers
    URL = args.URL
    PUBLISHERS = args.publishers
    LIMIT = args.limit
    SEARCHPATTERN = args.searchpattern
    LANGUAGE = args.language
    OUTDIR = args.outdir
    VERBOSE = args.verbose
    
    match VERBOSE:
        case 0: 
            loglevel = logging.ERROR
        case 1:
            loglevel = logging.WARNING
        case 2:
            loglevel = logging.INFO
        case 3: 
            loglevel = logging.DEBUG
    
    logging.basicConfig(
    format='[%(asctime)s] - [%(levelname)s] - %(message)s', 
    level=loglevel, 
    datefmt='%d-%b-%y %H:%M:%S'
    )
    
    if LISTPUBLISHERS:
        pprint.pp(list(SETS.keys()))
        exit()

    records = Records(URL, PUBLISHERS)
    
    downloader = Downloader(OUTDIR)
    
    logging.debug("Start looping over records")
    for record in records:
        
        if record.counter == LIMIT:
            break
        
        if not record.filter(LANGUAGE, SEARCHPATTERN):
            continue  # Skip record and continue to next loop

        if not OUTDIR:
            pass
        else:
            for i in record.urls:
                downloader.url = i
        
    if not downloader.url:
        logging.debug("No downloads")
    else:
        downloader.threaded_download()
        
    logging.info("Finished queries. Total of %s queries, found %s matching records and downloaded %s files", 
                 records.idx, Record.counter, downloader._download_success)
    if downloader._download_success < downloader._download_attempt:
        logging.warning('Download of %s files failed', 
                        downloader._download_attempt-downloader._download_success)