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
oai-harvest.exe --help
```

## Example usage:

Download metadata and filelist using search pattern for `maaseutu` in abstracts, keywords or titles:  

```
oai-harvest https://julkaisut.valtioneuvosto.fi/oai/request -sp "[Mm]aa[-]?seu.*" -vv -m C:\Users\maxst\Desktop\MAAVALTA\metadata_maaseutu_07102024.csv -f C:\Users\maxst\Desktop\MAAVALTA\filelist_maaseutu_07102024.txt
```

Same for `kaupunki` search pattern:  

```
oai-harvest https://julkaisut.valtioneuvosto.fi/oai/request -sp "[Kk]au[-]?pun.*" -vv -m C:\Users\maxst\Desktop\MAAVALTA\metadata_kaupunki_07102024.csv -f C:\Users\maxst\Desktop\MAAVALTA\filelist_kaupunki_07102024.txt
```

Use helper script to download with multiple search-patterns  
```
./valto-haku.sh -m "../../metadatafiles" -f "../../filelistfiles" -s "15102024"
```

File list obtained by `-f` option can be used to download file with wget:  

```
# Move to download directory and download files from list of urls  
cd docs_maaseutu_07102024
wget -i ../filelist_maaseutu_07102024.txt
```

## TODO list:

- Replace file downloading option with save urls to list option -> can be used to download files with more reliable tools (eg. `wget -i filelist.txt`) DONE

- Remove downloader functionality   

- What about records with multiple files? NOT A PROBLEM WITH FILELIST

- Failure to download certain files, why? TRY TO DOWNLOAD FOLLOWING FILE WITH PYTHON: https://julkaisut.valtioneuvosto.fi/bitstream/10024/162066/4/Maa-%20ja%20mets%c3%a4talousministeri%c3%b6n%20strategia%202030.pdf IT IS IMPOSSIBLE!
