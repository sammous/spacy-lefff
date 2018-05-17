import os
import sys
import logging
import tarfile
import shutil
import requests
import re
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

    @staticmethod
    def get_filename_from_cd(cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        fname = re.findall('filename="(.+)"', cd)
        if len(fname) == 0:
            return None
        return fname[0]

    def _download_data(self):
        LOGGER.info('downloading data for {}...'.format(self.pkg))
        r = requests.get(self.url)
        filename = self.get_filename_from_cd(r.headers.get('content-disposition'))
        path = os.path.join(self.download_dir, filename)
        open(path, 'wb').write(r.content)
        if filename.endswith('.tar.gz'):
            tar = tarfile.open(path, "r:gz")
            for tarinfo in tar:
                tar.extract(tarinfo, self.download_dir)
            tar.close()
        #clean raw tar gz
        os.remove(path)
        LOGGER.info('download complete')


if __name__ == '__main__':
    d=  Downloader('tagger', url='https://www.dropbox.com/s/xjn863wq4599vur/model.tar.gz?dl=1')
