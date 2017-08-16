---
title: Scikit-learn Pipeline Persistence and JSON Serialization
date: 2016-04-11 17:04:42
read: 8
image: ./sources/pixel_art/scikit.png
---

*First off, I would like to thank Sebastian Raschka, and Chris Wagner for
providing the text and code that proved essential for writing this blog.
Read the follow-up to this post [here](./serialize-sk).*

For some time now, I have been wanting to replace simply pickling my
[`sklearn`](http://scikit-learn.org/stable/)
pipelines. [Pickle](https://docs.python.org/3.5/library/pickle.html) is
incredibly convenient, but can be easy to corrupt, is not very transparent, and
has [compatibility issues](https://bugs.python.org/issue6137). The latter has
been quite a thorn in my side for several projects, and I stumbled upon it again
while working on my own small text mining
[framework](https://www.github.com/cmry/omesa). Persistence is imperative when
deploying a pipeline to a practical application like demo. Each piece of new
data needs to be constructed in exactly the same vector size as it was offered in
during development. Therefore, feature extraction, hashing, normalization, etc.
has to be exactly the same, feeding data to the same model as after training.
After reading [Sebastian Raschka's notebook](http://nbviewer.jupyter.org/github/rasbt/python-machine-learning-book/blob/master/code/bonus/scikit-model-to-json.ipynb) on model persistence for scikit-learn,
I figured I might give it a go myself.

> Please note that all code is in Python 3.x, sklearn 0.17, and numpy 1.9.

## Recap: Classifier to JSON

I also tried to use [JSON](www.json.org) as storage format. In addition, however,
I aimed to store other parts of a pipeline as well. The biggest
hurdles are definitely due to [`numpy`](https://docs.scipy.org/doc/numpy-1.10.1/about.html).
These special Python objects cannot be serialized in JSON, as it is limited to
at most `bool`, `int`, `float`, and `str` for data types and `list`, and `dict`
for structures. Following Sebastian's notes, I first tried to reproduce this
to store classifiers. For trained models, we can access the parameters by
`get_params`, and fit information in the class attributes (e.g. `classes_`,
`intercept_` for `LogisticRegression`). Alternatively, we can just store all
class information as follows:

```python

from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris

iris = load_iris()
X, y = iris.data, iris.target

lr = LogisticRegression(multi_class='multinomial', solver='newton-cg')
lr.fit(X, y)

attr = lr.__dict__
attr

# output ---------

{'C': 1.0,
 'class_weight': None,
 'classes_': array([0, 1, 2]),
 'coef_': array([[-0.42363867,  0.96158336, -2.5193416 , -1.08640712],
        [ 0.5342659 , -0.31758963, -0.2054791 , -0.9392839 ],
        [-0.11062723, -0.64399373,  2.7248207 ,  2.02569101]]),
 'dual': False,
 'fit_intercept': True,
 'intercept_': array([  9.88272104,   2.21749429, -12.10021533]),
 'intercept_scaling': 1,
 'max_iter': 100,
 'multi_class': 'multinomial',
 'n_iter_': array([20], dtype=int32),
 'n_jobs': 1,
 'penalty': 'l2',
 'random_state': None,
 'solver': 'newton-cg',
 'tol': 0.0001,
 'verbose': 0,
 'warm_start': False}
```

Great, so the `_`-affixed keys are fit-parameters, whereas the rest are model
parameters. The first issue arises here, which is that some of our values have
a `numpy.array` that is incompatible with JSON. These are pretty straight-forward
to serialize, we can simply convert them to a list:

```python
import json

for k, v in attr.items():
    if isinstance(v, list) and v[-1:] == '_':
        attr[k] = v.tolist()

json.dump(attr, open('./attributes.json', 'w'))
```

And sure enough, if we port these back to a new instance of the
`LogisticRegression` class we are good to go:

```python
lr2 = LogisticRegression()
for k, v in attr.items():
    if isinstance(v, list):
        setattr(lr2, k, np.array(v))
    else:
        setattr(lr2, k, v)
lr2.predict(X)  # just for testing :)
```

Sadly, life isn't always this easy.

## Problem: Pipeline to JSON

In a broader scenario, one might use other `sklearn` classes to create a fancy
data-to-prediction pipeline. Say that we want to accept some text input, and
generate $n$-gram features. I wrote about using the `DictVectorizer` for
efficient gram extraction in my [previous post](https://cmry.github.io/notes/ngrams),
so I'll use it here:

```python
from collections import Counter

def extract_grams(sentence, n_list):
    tokens = sentence.split()
    return Counter([gram for gram in zip(*[tokens[i:]
                    for n in n_list for i in range(n)])])

```

Assume we have some form that accepts user input, represented by `text_input`,
and our training data `corpus`. First we extract features and fit the vectorizer:

```python
from sklearn.feature_extraction import DictVectorizer

corpus = ["this is an example", "hey more examples", "can we get more examples"]
text_input = "hey can I get more examples"

vec = DictVectorizer().fit([extract_grams(s, [2]) for s in corpus])

print(vec.transform(extract_grams(text_input, [2])))

# output ---------

(0, 2)	1.0
(0, 5)	1.0
```

Sweet, the vectorizer works. Now it can be serialized as before, right?

``` python
vec_attr = vec.__dict__
for k, v in vec_attr.items():
    if isinstance(v, list) and v[-1:] == '_':
        vec_attr[k] = v.tolist()
json.dump(vec_attr, open('./vec_attributes.json', 'w'))

# output ---------

TypeError: key ('more', 'examples') is not a string
```

Nope. The tuples used to fit the vectorizer are not in the data types accepted
by JSON. Ok, no problem, we just alter the `extract_grams` function again to
concatenate them to a string and run it again:

```python
def extract_grams(sentence, n_list):
    tokens = sentence.split()
    return Counter(['_'.join(list(gram)) for gram in zip(*[tokens[i:]
                    for n in n_list for i in range(n)])])

vec = DictVectorizer().fit([extract_grams(s, [2]) for s in corpus])

vec_attr = vec.__dict__
for k, v in vec_attr.items():
    if isinstance(v, list) and v[-1:] == '_':
        vec_attr[k] = v.tolist()
json.dump(vec_attr, open('./vec_attributes.json', 'w'))

# output ---------

TypeError: <class 'numpy.float64'> is not JSON serializable
```

Uh oh.

## Serializing Most of Numpy

Life is not simple, and neither is scikit-learn. Actually, from a range of
pipeline pieces I have tested, there are many different sources that throw JSON
serialization errors. These can be variables that store types, or any other
`numpy` data format (`np.int32` and `np.float64` are both used in `LinearSVC`
for example). While some objects have a (limited) python object representation,
one of the harder cases was the error thrown by the `DictVectorizer`. To
convert a `numpy` type object, the following is required:

```python
target = np.float64
serialisation = target.__name__
deserialisation = np.dtype(serialisation).type
print(target, serialisation, deserialisation)

# output ---------

<class 'numpy.float64'> float64 <class 'numpy.float64'>
```

So, we actually need a couple of functions that can `serialize` an entire
dictionary with python and `numpy` objects, and then `deserialize` when we need
it again. I was very much helped by [Chris Wagner's blog](http://robotfantastic.org/serializing-python-data-to-json-some-edge-cases.html), who already
provides quite a big code snippet that does exactly this. I inserted the
following lines myself:

```python

def serialize(data):
    ...
    if isinstance(data, type):
        return {"py/numpy.type": data.__name__}
    if isinstance(data, np.integer):
        return {"py/numpy.int": int(data)}
    if isinstance(data, np.float):
        return {"py/numpy.float": data.hex()}
    ...

def deserialize(data):
    ...
    if "py/numpy.type" in dct:
        return np.dtype(dct["py/numpy.type"]).type
    if "py/numpy.int" in dct:
        return np.int32(dct["py/numpy.int"])
    if "py/numpy.float" in dct:
        return np.float64.fromhex(dct["py/numpy.float"])
    ...
```

This even retains the floating point
precisions by hexing them for serialization. So using these scripts, we can
run the full pipeline by importing Chris' script with my alterations as
`serialize_json`. First we fit our amazing corpus again, and train the model:

```python
import json
import numpy as np
import serialize_sk as sr
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC

corpus = ["this is an example", "hey more examples", "can we get more examples"]

def extract_grams(sentence, n_list):
    tokens = sentence.split()
    return Counter(['_'.join(list(gram)) for gram in zip(*[tokens[i:]
                    for n in n_list for i in range(n)])])

vec = DictVectorizer()
D = vec.fit_transform([extract_grams(s, [2]) for s in corpus])

svm = LinearSVC()
svm.fit(D, [1, 0, 1])
atb_vec = vec.__dict__
atb_clf = svm.__dict__
```

Serialize the vectorizer and model:

```python
def serialize(d, name):
    for k, v in d.items():
        d[k] = sr.data_to_json(v)
    json.dump(d, open(name + '.json', 'w'))

serialize(atb_clf, 'clf')
serialize(atb_vec, 'vec')
```

Now we assume that this a new application. First, we load the `.json`s and
deserialize:

```python
new_vec = json.load(open('vec.json'))
new_clf = json.load(open('clf.json'))


def deserialize(class_init, attr):
    for k, v in attr.items():
        setattr(class_init, k, sr.json_to_data(v))
    return class_init

vec2 = deserialize(DictVectorizer(), new_vec)
svm2 = deserialize(LinearSVC(), new_clf)
```

And finally we accept user input, and give back a classification label:

```python
user_input = "hey can I get more examples"

grams = vec2.transform(extract_grams(user_input, [2]))
print(grams, "\n")
print(svm2.predict(grams))

# output ---------
(0, 2)	1.0
(0, 5)	1.0

[1]
```

And it works!

## Conclusion

Chances are that when using different classes in `sklearn`, other
issues might present themselves. However, for now I've got my most used pieces
covered. It will probably mostly entail refining `serialize_json`. Of course, even
when using JSON there is no protection from the fact that parameters might be
changed in different version of scikit-learn. At least now the JSONs stored
with old versions are transparent
enough to be easily modifiable. Any suggestions and or improvements are
obviously more than welcome. I hereby also provide [my version](https://github.com/cmry/cmry.github.io/tree/master/sources/serialize_sk.py) of Chris Wagner's
script, as well as a Jupyter [notebook](https://github.com/cmry/cmry.github.io/tree/master/sources/serialize_sk.ipynb).
