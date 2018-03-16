
#!/usr/bin/env python
# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
from setuptools import setup, find_packages


def setup_package():
    package_name = 'spacy_lefff'
    root = Path(__file__).parent.resolve()

    # Get readme
    readme_path = root / 'README.md'
    with readme_path.open('r', encoding='utf8') as f:
        readme = f.read()

    setup(
        name='spacy-lefff',
        description=' Custom French lemmatizer based on Leff for spacy',
        long_description=readme,
        author='sami moustachir',
        author_email='moustachir.sami@gmail.com',
        url='https://github.com/sammous/spacy-lefff',
        version='0.1',
        license='MIT',
        packages=find_packages(),
        install_requires=[
            'spacy>=2.0.0,<3.0.0'],
        zip_safe=False,
        tests_require=['pytest']
    )


if __name__ == '__main__':
    setup_package()
