# webscraper

Command line tools for collecting data from web-services

Currently contains tool for harvesting data from Finnish Kansalliskirjasto OAI-PMH service.

## Installation

```
pip install git+https://github.com/StranMax/webscraper.git@master
```

Requisites: python>=3.12

## Usage

```
oai_harvest.exe --help
```

## Example usage:

Download all files and metadata of records containing `maaseutu` in abstract or keywords:  

```
oai-harvest https://julkaisut.valtioneuvosto.fi/oai/request -sp "[Mm]aa[-]?seu.*" -vv -o C:\Users\maxst\Desktop\MAAVALTA\documents -m C:\Users\maxst\Desktop\MAAVALTA\metadata.csv
```

## TODO list:

- What about records with multiple files?

- Failure to download certain files, why?