# spacy-lefff : Custom French POS and lemmatizer based on Lefff for spacy [![Build Status](https://travis-ci.org/sammous/spacy-lefff.svg?branch=master)](https://travis-ci.org/sammous/spacy-lefff)[![Coverage Status](https://codecov.io/gh/sammous/spacy-lefff/badge.svg?branch=master)](https://codecov.io/gh/sammous/spacy-lefff?branch=master)

[spacy v2.0](https://spacy.io/usage/v2) extension and pipeline component for adding a French POS and lemmatizer based on Lefff.

## Description

This package allows to bring Lefff lemmatization and part-of-speech tagging to a spaCy custom pipeline.
When POS tagging and Lemmatizaion are combined inside a pipeline, it improves your text preprocessing for French compared to the built-in spaCy French processing.

## Installation

`spacy-lefff` requires `spacy` <= v2.0.9.

```
pip install spacy-lefff
```

## Usage

Import and initialize your `nlp` spacy object and add the custom component after it parsed the document so you can benefit the POS tags.
Be aware to work with `UTF-8`.

If both POS and lemmatizer are bundled, you need to tell the lemmatizer to use MElt mapping by setting `after_melt`, else it will use the spaCy part of speech mapping.
Current mapping used spaCy to Lefff is :

```json
{
    'ADJ': 'adj',
    'ADP': 'det',
    'ADV': 'adv',
    'DET': 'det',
    'PRON': 'cln',
    'PROPN': 'np',
    'NOUN': 'nc',
    'VERB': 'v',
    'PUNCT': 'poncts'
}
```

### Code snippet

You need to install the French spaCy package before : `python -m spacy download fr`.

```python
import spacy
from spacy_lefff import LefffLemmatizer, POSTagger

nlp = spacy.load('fr')
pos = POSTagger()
french_lemmatizer = LefffLemmatizer(after_melt=True)
nlp.add_pipe(pos, name='pos', after='parser')
nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')
doc = nlp(u"Qu'est ce qu'il se passe")
for d in doc:
    print(d.text, d.pos_, d._.melt_tagger, d._.lefff_lemma, d.tag_, d.lemma_)
```
## Credits

Sagot, B. (2010). [The Lefff, a freely available and large-coverage morphological and syntactic lexicon for French](https://hal.inria.fr/inria-00521242/). In 7th international conference on Language Resources and Evaluation (LREC 2010).

Benoît Sagot Webpage about LEFFF<br/>
http://alpage.inria.fr/~sagot/lefff-en.html<br/>

First work of [Claude Coulombe](https://github.com/ClaudeCoulombe) to support Lefff with Python : https://github.com/ClaudeCoulombe
