---
title: Scikit-learn Pipeline Persistence and JSON Serialization Part II
date: 2016-04-14 18:38:05
read: 5
---

*This is a follow-up to [this](./serialize) post.*

In my last entry, I wrote about several hurdles on the way to replacing pickle
with JSON for storing scikit-learn pipelines. While my previous solution was
satisfactory for handling a class per file, storing an entire pipeline
introduces more complexity than I previously assumed. In this follow-up, I will
quickly illustrate one of these issues, and provide an effective solution.

> Please note that all code is in Python 3.x, sklearn 0.17, and numpy 1.9.

## Quick Recap

We left off using `__dict__` representations for each of the `scikit-learn`
classes, converting their data structures (including those from `numpy`) with
a small script and storing them per pipeline item. This would make a final
application look as follows:

```python
vec = deserialize(DictVectorizer(), json.load(open('vec.json')))
svm = deserialize(LinearSVC(), json.load(open('clf.json')))

user_input = "hey can I get more examples"

grams = vec.transform(extract_grams(user_input, [2]))
print(svm.predict(grams))

# output ---------

[1]
```

The assumptions are that 1) your pipeline is quite small, so it's not too
convoluted to store their items separately, and 2) it has a static components,
e.g. it will always use an SVM, and not do any preprocessing. If you're
interested in reproducibility only, this is good enough. For demos, however,
flexibility can be important.

## Drop-in Models
Let's say we want to *just* allow selection of a trained model. The easiest
way would be to store the pipeline in a dictionary, for example:

```python
pipeline = {
    "clf": NaiveBayes(),
    "vec": DictVectorizer(),
}
```

It shouldn't really matter what `clf` is, as long as it has the same
methods as all other `sklearn` classes. Subsequently, our application can be
reduced to the following:

```python
pl = deserialize(Pipeline(), json.load(open('pipeline.json')))

user_input = "hey can I get more examples"
grams = pl['vec'].transform(extract_grams(user_input, [2]))
print(pl['clf'].predict(grams))
```

However, to achieve this, we would need to serialize the classes in a way that
we can deserialize them to their initialized form. Hence, just storing them as
their `__dict__` representation is not enough.

## Problem: Serializing Python Objects

How does one store a python object in a form that JSON can handle, and we can
deserialize in our application? Remember that before, we set classes like so:

```python
def deserialize(class_init, attr):
    for k, v in attr.items():
        setattr(class_init, k, sr.json_to_data(v))
    return class_init
```

We already know how to set the attributes (with `__dict__`), but we need a way
to get a representation from a class object which we can use to initialize it.
Python allows you to get a string name with `__class__`:

```python
vec = DictVectorizer()
print(str(vec.__class__))
print(vec.__class__.__name__)
print(vec.__module__)

# output ---------

"<class 'sklearn.feature_extraction.dict_vectorizer.DictVectorizer'>"
'DictVectorizer'
'sklearn.feature_extraction.dict_vectorizer'
```

As we can see from the output, the first returns a class object, and the second
its name. However, we would need the full path in order to import it, which
leaves us with having combine the latter two. From there, we could easily import
and initialize it by string:

```python
import sys

class_ = getattr(sys.modules[vec.__module__], vec.__class__.__name__)

new_vec = class_()
new_vec

# output ---------

DictVectorizer(dtype=<class 'numpy.float64'>, separator='=', sort=True,
               sparse=True)
```

After, we can use `setattr` again (like in the `deserialize` function above) to
return our settings. Just need to store them both in a format along with the
`__dict__` to pass to the deserializer. Something like:

```python
import json

def serialize_class(cls_):
    return sr.data_to_json({'mod': cls_.__module__,
                            'name': cls_.__class__.__name__,
                            'attr': cls_.__dict__})

def deserialize_class(cls_repr):
    cls_repr = sr.json_to_data(cls_repr)
    cls_ = getattr(sys.modules[cls_repr['mod']], cls_repr['name'])
    cls_init = cls_()
    for k, v in cls_repr['attr'].items():
        setattr(cls_init, k, v)
    return cls_init

cls_str = serialize_class(vec)
json.dump(cls_str, open('./vec_class.json', 'w'))

cls_js = json.load(open('./vec_class.json'))
deserialize_class(cls_js)

# output ---------

DictVectorizer(dtype=<class 'numpy.float64'>, separator='=', sort=True,
        sparse=True)
```

Great! Now the classes can be used in a pipeline dictionary.
As the [script](https://github.com/cmry/cmry.github.io/blob/master/sources/serialize_sk.py) I provided
in the previous post is recursive, these methods can be built in without much
effort. However, while reading into these object serialization techniques I
found an even better alternative (given that you don't mind dependencies).

## Conclusion and Package

So far I managed to manually convert most `numpy` cases in scikit-learn's
modules, and store them in dictionaries for
flexibility. However, I decided to sweep all of this off the table for
[jsonpickle](https://github.com/jsonpickle/jsonpickle). This package covers a
*lot* more edge-cases with a way more extensive implementation. Quick
demonstration:

```python
import jsonpickle

vec_repr = jsonpickle.encode(vec)
vec_repr

# output ---------

'{"py/object": "sklearn.feature_extraction.dict_vectorizer.DictVectorizer",
  "sparse": true, "sort": true, "separator": "=", "dtype":
  {"py/type": "numpy.float64"}}'
```

And with a quick `decode` we're back to our old python storage format!

That's it
for now, if I encounter any more challenges there will be another follow-up. As
before, I've written this up in a Jupyter [notebook](https://github.com/cmry/cmry.github.io/blob/master/sources/serialize_sk2.ipynb).
