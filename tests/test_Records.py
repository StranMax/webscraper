
import pytest

from sickle import Sickle
from webscraper.oai_harvester import Records, Record

@pytest.fixture
def julkaisut_valtioneuvosto_kk_metadata():
    sickle = Sickle('https://julkaisut.valtioneuvosto.fi/oai/request')
    records = sickle.ListRecords(metadataPrefix='kk')
    records.next()  # First record
    return records.next()  # Second record
    
def test_Records_next(julkaisut_valtioneuvosto_kk_metadata):
    records = Records('https://julkaisut.valtioneuvosto.fi/oai/request', None)
    next(records)  # First record
    # Second record
    assert next(records).title == Record(julkaisut_valtioneuvosto_kk_metadata).title