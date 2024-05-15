
import pytest

from sickle import Sickle
from webscraper.oai_harvester import Records, Record


@pytest.fixture
def kk_metadata():
    sickle = Sickle('https://julkaisut.valtioneuvosto.fi/oai/request')
    records = sickle.ListRecords(metadataPrefix='kk')
    return records
    
    
@pytest.fixture
def records_data():
    records = Records('https://julkaisut.valtioneuvosto.fi/oai/request', None)
    return records
    
    
def test_Records_next(kk_metadata, records_data):
    next(records_data)  # First record
    next(records_data)  # Second record
    
    kk_metadata.next()  # First record
    kk_metadata.next()  # Second record
    
    title_records_data = next(records_data).title  # Title from third record
    title_kk_metadata = Record(kk_metadata.next()).title  # Title from third record
    
    assert title_records_data == title_kk_metadata
    
def test_Records_idx(kk_metadata, records_data):
    
    for i in range(5):
        try:
            if i == 4:
                raise StopIteration
            assert records_data.idx == i
            next(records_data)
        except StopIteration:
            break
    
    
#def test_Records_Record_idx(records_data):

    #for _ in range(5):
        #rec = next(records_data)
        #assert records_data.idx == rec.counter-1
        #record = next(records)
        #record_idx = record.idx
        #records_idx = records.idx
        #assert records_idx == record_idx