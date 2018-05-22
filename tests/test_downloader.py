# coding: utf-8
from __future__ import unicode_literals

import os
import io
import pytest
import tarfile
import tempfile
from mock import patch, Mock, MagicMock
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
        raise_for_status=None,
        iter_content=None):
    '''
    Mocking get requests response.
    '''
    mock_resp = Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.headers = headers
    mock_resp.iter_content = MagicMock()
    mock_resp.iter_content.__iter__.return_value = iter_content 
    # add json data if provided
    if json_data:
        mock_resp.json = Mock(
            return_value=json_data
        )
    return mock_resp

@pytest.fixture(scope='session')
def _tmp_dir(tmpdir_factory):
    '''
    Creating a tar file from a test file in a tmp folder.
    '''
    dirtmp = tmpdir_factory.mktemp('models')
    tmpfile = dirtmp.join('model')
    tmpfile.write('TEST')
    tar = tarfile.open(os.path.join(dirtmp.strpath, "model.tar.gz"), "w:gz")
    tar.add(tmpfile.strpath, 'model')
    tar.close()
    os.remove(tmpfile.strpath)
    return dirtmp

@patch('spacy_lefff.downloader.requests.get')
@patch('spacy_lefff.downloader.tarfile')
def test_downloader(mock_tarfile, mock_get, _tmp_dir):
    content_disposition = 'attachment; filename="model.tar.gz"; filename*=UTF-8''model.tar.gz'
    model_tarfile = tarfile.open(os.path.join(_tmp_dir.strpath, 'model.tar.gz'), 'r:gz')
    headers = {'content-disposition': content_disposition, 'content-length': 100000}
    mock_resp = _mock_response(headers=headers)
    mock_get.return_value = mock_resp
    mock_tarfile.open.return_value = model_tarfile 
    d = Downloader('test', download_dir=_tmp_dir.strpath, url=URL_MODEL)
    test_folder = os.path.join(_tmp_dir.strpath, 'test')
    m = os.path.join(test_folder, 'model')
    assert len(_tmp_dir.listdir()) == 2 #test folder, temp model tar
    f = io.open(m, mode='r', encoding='utf-8')
    #checking if untar model is the same as the one in _tmp_dir tar file
    assert unicode(f.read()) == 'TEST'

@patch('spacy_lefff.downloader.requests.get')
def test_downloader_failed(mock_get, _tmp_dir):
    mock_resp = _mock_response()
    mock_get.return_value = mock_resp
    with pytest.raises(Exception) as e_info:
        d = Downloader('test', download_dir=_tmp_dir.strpath, url='')
        assert e_info.value.message == "Couldn't fetch model data."
