
import pytest

from webscraper.oai_harvester import Records, Record, Downloader


@pytest.fixture
def records_data():
    records = Records('https://julkaisut.valtioneuvosto.fi/oai/request', None)
    return records
    
    
#def test_Downloader_counters(records_data):
    
    