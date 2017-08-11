---
title: Resources
---

Code, notebooks, and data I made openly available. Quick overview:

### Code

* Omesa - small framework for reproducible Text Mining research

* topbox - wrapper for Labelled Latent Dirichlet Allocation (L-LDA)

* markdoc - convert NumPy-styled Python docstring to Markdown

* ebacs - minimalistic conference manager

* ec2latex - XML to LaTeX book of abstracts

----

## Omesa

<a href="http://github.com/cmry/omesa"><i class="fa fa-github"></i></a>  &nbsp;  <a href="http://omesa.readthedocs.org/"><i class="fa fa-book"></i></a>

A small framework for reproducible Text Mining research that largely builds
on top of scikit-learn. Its goal is to make common research procedures fully
automated, optimized, and well recorded. To this end it features:

- Exhaustive search over best features, pipeline options, to classifier optimization.

- Flexible wrappers to plug in your tools and features of choice.

- Completely sparse pipeline through hashing - from data to feature space.

- Record of all settings and fitted parts of the entire experiment, promoting reproducibility.

- Dump an easily deployable version of the final model for plug-and-play demos.

End-to-End classification in 2 minutes:

``` python
from omesa.experimeomesant import Experiment
from omesa.featurizer import Ngrams

conf = {
    "gram_experiment": {
        "name": "gram_experiment",
        "train_data": ["./n_gram.csv"],
        "has_header": True,
        "features": [Ngrams(level='char', n_list=[3])],
        "text_column": 1,
        "label_column": 0,
        "folds": 10,
        "save": ("log")
    }
}

for experiment, configuration in conf.items():
    Experiment(configuration)
```

Output:

``` bash
---- Omesa ----

 Config:

        feature:   char_ngram
        n_list:    [3]

    name: gram_experiment
    seed: 111

 Sparse train shape: (20, 1287)

 Tf-CV Result: 0.8
```

## markdoc

<a href="http://github.com/cmry/markdoc"><i class="fa fa-github"></i></a>

This piece of code can be used to convert NumPy-styled Python docstrings
(example), such as those used in scikit-learn, to Markdown with minimum
dependencies. In this way, only the code-contained documentation needs to be
editted, and your documentation on for example readthedocs can be automatically
updated thereafter with some configuration.

Simply type:

``` bash
python3 markdoc.py /dir/to/somefile.py /dir/to/somedoc.md
```


## topbox

<a href="http://github.com/cmry/topbox"><i class="fa fa-github"></i></a>

A small Python 3 wrapper around the Stanford Topic Modeling Toolbox (STMT) that
makes working with L-LDA a bit easier; no need to leave the Python environment.
More information on its workings can be found on my [blog](https://cmry.github.io/2015/06/18/shed/).
Code sample:

{% highlight python %}
import topbox

stmt = topbox.STMT('bit_of_testing', epochs=10, mem=15000)

X = ['text text more text', 'things to do with text']
y = ['label1 label2', 'label1 label3']

stmt.train(space, labels)

infer = ['this is a text', 'things with more text']
gs = ['label1 label2', 'label1 label3']

stmt.test(infer, gs)

y_true, y_score = stmt.results(gs, array=True)
print(average_precision_score(y_true, y_score))
{% endhighlight %}

## ebacs

<a href="http://github.com/cmry/ebacs"><i class="fa fa-github"></i></a> &nbsp; *in development*

Minimal working version of a [bottle.py](http://http://www.bottlepy.org/)
front-end to [ec2latex](http://github.com/cmry/ec2latex). Currently, it demonstrates how
conference attendees can submit their abstracts (can include LaTeX code) via a form, after
which this submission is added to the database. From the front page, the book of abstracts
can be compiled per demonstration. The idea is that this functionality is
embeddable for your conference website. Requires `bottle`, `cork`, `beaker` and `blitzdb`.

![twitter](/assets/img/ebacs.png)

## ec2latex

<a href="http://github.com/cmry/ec2latex"><i class="fa fa-github"></i></a>

Python tool for converting XML-based confrence submissions (such as EasyChair)
to a full LaTeX book of abstracts. Sample of the end result can be found [here](http://www.clips.uantwerpen.be/~ben/sites/default/files/book_of_abstracts_final.pdf).
After manual work on the `.tex` files (can be found in github README),
can be simply called with:

    python ec2latex.py

This code has been integrated into [ebacs](https://www.github.com/cmry/ebacs).
