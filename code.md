---
layout: post
title: Resources
mast: code
---

Code, notebooks, and data I made openly available. Quick overview:

### Code
* shed - wrapper for Labelled Latent Dirichlet Allocation
* ebacs - minimalistic conference manager
* ec2latex - XML to LaTeX book of abstracts

----

## shed

<a href="http://github.com/cmry/shed"><i class="fa fa-github"></i></a>

A small Python 3 wrapper around the Stanford Topic Modeling Toolbox (STMT) that
makes working with L-LDA a bit easier; no need to leave the Python environment.
More information on its workings can be found on my [blog](https://cmry.github.io/2015/06/18/shed/).
Code sample:

{% highlight python %}
import shed

stmt = shed.STMT('bit_of_testing', epochs=10, mem=15000)

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

{% highlight shell %}
python ec2latex.py
{% endhighlight %}

This code has been integrated into [ebacs](https://www.github.com/cmry/ebacs).
