# spacy-lefff : Custom French lemmatizer based on Lefff for spacy [![Build Status](https://travis-ci.org/sammous/spacy-lefff.svg?branch=master)](https://travis-ci.org/sammous/spacy-lefff)[![Coverage Status](https://codecov.io/gh/sammous/spacy-lefff/badge.svg?branch=master)](https://codecov.io/gh/sammous/spacy-lefff?branch=master)

[spacy v2.0](https://spacy.io/usage/v2) extension and pipeline component for adding a French lemmatizer based on Lefff.

## Installation

`spacy-lefff` requires `spacy` v2.0.0 or higher.

(not yet deployed to `PyPi`)

```
pip install spacy-lefff
```

## Usage

Import and initialize your `nlp` spacy object and add the custom component after it parsed the document so you can benefit the POS tags.

```python
from spacy_lefff import LefffLemmatizer

nlp = spacy.load('fr')
french_lemmatizer = LefffLemmatizer()
nlp.add_pipe(french_lemmatizer, name='lefff', after='parser')
doc = nlp(u"Paris est une ville très chère.")
for d in doc:
    print(d.text, d.pos_, d._.lefff_lemma, d.tag_)
```
## Credits

Sagot, B. (2010). [The Lefff, a freely available and large-coverage morphological and syntactic lexicon for French](https://hal.inria.fr/inria-00521242/). In 7th international conference on Language Resources and Evaluation (LREC 2010).

Benoît Sagot Webpage about LEFFF<br/>
http://alpage.inria.fr/~sagot/lefff-en.html<br/>

First work of [Claude Coulombe](https://github.com/ClaudeCoulombe) to support Lefff with Python : https://github.com/ClaudeCoulombe
