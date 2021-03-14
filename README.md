[![Build Status](https://travis-ci.org/sammous/spacy-lefff.svg?branch=master)](https://travis-ci.org/sammous/spacy-lefff)[![Coverage Status](https://codecov.io/gh/sammous/spacy-lefff/badge.svg?branch=master)](https://codecov.io/gh/sammous/spacy-lefff?branch=master)[![PyPI version](https://badge.fury.io/py/spacy-lefff.svg)](https://badge.fury.io/py/spacy-lefff)

# spacy-lefff : Custom French POS and lemmatizer based on Lefff for spacy

[spacy v2.0](https://spacy.io/usage/v2) extension and pipeline component for adding a French POS and lemmatizer based on [Lefff](https://hal.inria.fr/inria-00521242/).

_On version [v2.0.17](https://github.com/explosion/spaCy/releases/tag/v2.0.17), spaCy updated French lemmatization_

_As of version *0.4.0* and above, `spacy-lefff` only supports python3.6+ and spacy v3_

## Description

This package allows to bring Lefff lemmatization and part-of-speech tagging to a spaCy custom pipeline.
When POS tagging and Lemmatizaion are combined inside a pipeline, it improves your text preprocessing for French compared to the built-in spaCy French processing.
It is still a WIP (work in progress), so the matching might not be perfect but if nothing was found by the package, it is still possible to use the default results of `spaCy`.

## Installation

`spacy-lefff` requires `spacy` >= v3.0.0.

```
pip install spacy-lefff
```

## Usage

Import and initialize your `nlp` spacy object and add the custom component after it parsed the document so you can benefit the POS tags.
Be aware to work with `UTF-8`.

If both POS and lemmatizer are bundled, you need to tell the lemmatizer to use MElt mapping by setting `after_melt`, else it will use the spaCy part of speech mapping.

`default` option allows to return the word by default if no lemma was found.

Current mapping used spaCy to Lefff is :

```json
{
    "ADJ": "adj",
    "ADP": "det",
    "ADV": "adv",
    "DET": "det",
    "PRON": "cln",
    "PROPN": "np",
    "NOUN": "nc",
    "VERB": "v",
    "PUNCT": "poncts"
}
```

## MElt Tagset

MElt Tag table:

```
ADJ 	   adjective
ADJWH	   interrogative adjective
ADV	   adverb
ADVWH	   interrogative adverb
CC	   coordination conjunction
CLO	   object clitic pronoun
CLR	   reflexive clitic pronoun
CLS	   subject clitic pronoun
CS	   subordination conjunction
DET	   determiner
DETWH	   interrogative determiner
ET	   foreign word
I	   interjection
NC	   common noun
NPP	   proper noun
P	   preposition
P+D	   preposition+determiner amalgam
P+PRO	   prepositon+pronoun amalgam
PONCT	   punctuation mark
PREF	   prefix
PRO	   full pronoun
PROREL	   relative pronoun
PROWH	   interrogative pronoun
V	   indicative or conditional verb form
VIMP	   imperative verb form
VINF	   infinitive verb form
VPP	   past participle
VPR	   present participle
VS	   subjunctive verb form
```

### Code snippet

You need to install the French spaCy package before : `python -m spacy download fr`.

-   An example using the `LefffLemmatizer` without the `POSTagger`:

```python
import spacy
from spacy_lefff import LefffLemmatizer
from spacy.language import Language

@Language.factory('french_lemmatizer')
def create_french_lemmatizer(nlp, name):
    return LefffLemmatizer()

nlp = spacy.load('fr_core_news_sm')
nlp.add_pipe('french_lemmatizer', name='lefff')
doc = nlp(u"Apple cherche a acheter une startup anglaise pour 1 milliard de dollard")
for d in doc:
    print(d.text, d.pos_, d._.lefff_lemma, d.tag_, d.lemma_)
```

| Text     | spaCy POS | Lefff Lemma | spaCy tag                                                    | spaCy Lemma |
| -------- | --------- | ----------- | ------------------------------------------------------------ | ----------- |
| Apple    | ADJ       | None        | ADJ\_\_Number=Sing                                           | Apple       |
| cherche  | NOUN      | cherche     | NOUN\_\_Number=Sing                                          | chercher    |
| a        | AUX       | None        | AUX\_\_Mood=Ind Number=Sing Person=3 Tense=Pres VerbForm=Fin | avoir       |
| acheter  | VERB      | acheter     | VERB\_\_VerbForm=Inf                                         | acheter     |
| une      | DET       | un          | DET\_\_Definite=Ind Gender=Fem Number=Sing PronType=Art      | un          |
| startup  | ADJ       | None        | ADJ\_\_Number=Sing                                           | startup     |
| anglaise | NOUN      | anglaise    | NOUN\_\_Gender=Fem Number=Sing                               | anglais     |
| pour     | ADP       | None        | ADP\_\_\_                                                    | pour        |
| 1        | NUM       | None        | NUM\_\_NumType=Card                                          | 1           |
| milliard | NOUN      | milliard    | NOUN\_\_Gender=Masc Number=Sing NumType=Card                 | milliard    |
| de       | ADP       | un          | ADP\_\_\_                                                    | de          |
| dollard  | NOUN      | None        | NOUN\_\_Gender=Masc Number=Sing                              | dollard     |

-   An example using the `POSTagger` :

```python
import spacy
from spacy_lefff import LefffLemmatizer, POSTagger
from spacy.language import Language

@Language.factory('french_lemmatizer')
def create_french_lemmatizer(nlp, name):
    return LefffLemmatizer(after_melt=True, default=True)

@Language.factory('melt_tagger')  
def create_melt_tagger(nlp, name):
    return POSTagger()
 
nlp = spacy.load('fr_core_news_sm')
nlp.add_pipe('melt_tagger', after='parser')
nlp.add_pipe('french_lemmatizer', after='melt_tagger')
doc = nlp(u"Apple cherche a acheter une startup anglaise pour 1 milliard de dollard")
for d in doc:
    print(d.text, d.pos_, d._.melt_tagger, d._.lefff_lemma, d.tag_, d.lemma_)
```

| Text     | spaCy POS | MElt Tag | Lefff Lemma | spaCy tag                                                    | spaCy Lemma |
| -------- | --------- | -------- | ----------- | ------------------------------------------------------------ | ----------- |
| Apple    | ADJ       | NPP      | apple       | ADJ\_\_Number=Sing                                           | Apple       |
| cherche  | NOUN      | V        | chercher    | NOUN\_\_Number=Sing                                          | chercher    |
| a        | AUX       | V        | avoir       | AUX\_\_Mood=Ind Number=Sing Person=3 Tense=Pres VerbForm=Fin | avoir       |
| acheter  | VERB      | VINF     | acheter     | VERB\_\_VerbForm=Inf                                         | acheter     |
| une      | DET       | DET      | un          | DET\_\_Definite=Ind Gender=Fem Number=Sing PronType=Art      | un          |
| startup  | ADJ       | NC       | startup     | ADJ\_\_Number=Sing                                           | startup     |
| anglaise | NOUN      | ADJ      | anglais     | NOUN\_\_Gender=Fem Number=Sing                               | anglais     |
| pour     | ADP       | P        | pour        | ADP\_\_\_                                                    | pour        |
| 1        | NUM       | DET      | 1           | NUM\_\_NumType=Card                                          | 1           |
| milliard | NOUN      | NC       | milliard    | NOUN\_\_Gender=Masc Number=Sing NumType=Card                 | milliard    |
| de       | ADP       | P        | de          | ADP\_\_\_                                                    | de          |
| dollard  | NOUN      | NC       | dollard     | NOUN\_\_Gender=Masc Number=Sing                              | dollard     |

We can see that both `cherche` and `startup` where not tagged correctly by the default pos tagger.
`spaCy`classified them as a `NOUN` and `ADJ` while `MElT` classified them as a `V` and an `NC`.

## Credits

Sagot, B. (2010). [The Lefff, a freely available and large-coverage morphological and syntactic lexicon for French](https://hal.inria.fr/inria-00521242/). In 7th international conference on Language Resources and Evaluation (LREC 2010).

Benoît Sagot Webpage about LEFFF<br/>
http://alpage.inria.fr/~sagot/lefff-en.html<br/>

First work of [Claude Coulombe](https://github.com/ClaudeCoulombe) to support Lefff with Python : https://github.com/ClaudeCoulombe
