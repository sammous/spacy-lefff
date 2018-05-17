# coding: utf-8
from __future__ import unicode_literals

import os
import pytest
import tarfile
import tempfile
from mock import patch, Mock
import requests
from spacy_lefff import Downloader
from spacy_lefff.melt_tagger import URL_MODEL

def test_url_model():
    assert requests.get(URL_MODEL).status_code == 200

def test_get_filename_from_cd():
    cd = 'attachment; filename="model.tar.gz"; filename*=UTF-8''model.tar.gz'
    assert Downloader.get_filename_from_cd(cd) == 'model.tar.gz'

def _mock_response(
        status=200,
        content="CONTENT",
        json_data=None,
        headers=None,
        raise_for_status=None):
    mock_resp = Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.headers = headers
    # add json data if provided
    if json_data:
        mock_resp.json = Mock(
            return_value=json_data
        )
    return mock_resp

@pytest.fixture(scope='session')
def _tmp_dir(tmpdir_factory):
    dirtmp = tmpdir_factory.mktemp('models')
    tmpfile = dirtmp.join('model')
    tmpfile.write('TEST')
    tar = tarfile.open(os.path.join(dirtmp.strpath, "model.tar.gz"), "w:gz")
    tar.add(tmpfile.strpath, 'model')
    tar.close()
    return dirtmp

@patch('spacy_lefff.downloader.requests.get')
def test_downloader(mock_get, _tmp_dir):
    content_disposition = 'attachment; filename="model.tar.gz"; filename*=UTF-8''model.tar.gz'
    model = open(os.path.join(_tmp_dir.strpath, 'model.tar.gz'), 'rb')
    mock_resp = _mock_response(content=model.read(), headers={'content-disposition': content_disposition})
    mock_get.return_value = mock_resp
    d = Downloader('test', download_dir=_tmp_dir.strpath, url=URL_MODEL)
    m = _tmp_dir.listdir()[0].listdir()[0]
    assert len(_tmp_dir.listdir()) == 3 #test folder, temp model file, tar
    f = open(m.strpath, 'rb')
    assert f.read() == 'TEST'
