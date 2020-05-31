import os
import sys
import logging
import tarfile
import shutil
import requests
import re
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
LOGGER = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, pkg, url=None, download_dir=DATA_DIR):
        self._error = None
        self.url = url
        self.pkg = pkg
        if not os.path.exists(os.path.join(download_dir, pkg)):
            os.mkdir(os.path.join(download_dir, pkg))
            self.download_dir = os.path.join(os.path.join(download_dir, pkg))
            self._download_data()
        else:
            LOGGER.info('data already set up')

    def _download_data(self):
        LOGGER.info('downloading data for {}...'.format(self.pkg))
        r = requests.get(self.url, stream=True)
        total_length = r.headers.get('content-length', 0)
        pbar = tqdm(
                unit='B', unit_scale=True,
                total=int(total_length))
        if total_length is None:
            LOGGER.error("Couldn't fetch model data.")
            raise Exception("Couldn't fetch model data.")
        else:
            filename = 'model.tar.gz'
            path = os.path.join(self.download_dir, filename)
            with open(path, 'wb') as f:
                for data in r.iter_content(chunk_size=4096):
                    f.write(data)
                    pbar.update(len(data))
            if filename.endswith('.tar.gz'):
                tar = tarfile.open(path, "r:gz")
                for tarinfo in tar:
                    tar.extract(tarinfo, self.download_dir)
                tar.close()
            # clean raw tar gz
            os.remove(path)
            LOGGER.info('download complete')
