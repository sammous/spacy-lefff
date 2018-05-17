# coding: utf-8
from __future__ import unicode_literals

import pytest
from mock import patch
import requests
from spacy_lefff import Downloader
from spacy_lefff.melt_tagger import URL_MODEL

def test_url_model():
    assert requests.get(URL_MODEL).status_code == 200

@patch('spacy_lefff.Downloader._download_data')
def test_downloader(download, tmpdir_factory):
    dirtmp = tmpdir_factory.mktemp('dirtest').getbasetemp().strpath
    d = Downloader('test', download_dir=tmpdir, url=URL_MODEL)
    assert download.called
    assert len(dirtmp.listdir()) == 1
