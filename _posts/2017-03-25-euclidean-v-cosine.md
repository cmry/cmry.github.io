---
title: SDM - Euclidean vs. Cosine Distance
date: 2017-03-25 18:27:10
read: 5
---

*This post was written as a reply to a question asked in the
[Social Data Mining](https://github.com/tcsai/social-data-mining) course.*

> When to use the cosine similarity?

Let's compare two different measures of distance in a vector space, and why either has its function under different circumstances. Starting off with quite a straight-forward example, we have our vector space `X`, that contains instances with animals. They are measured by their `length`, and `weight`. They have also been labelled by their stage of aging (`young = 0`, `mid = 1`, `adult = 2`). Here's some random data:


```python
import numpy as np

X = np.array([[6.6, 6.2, 1],
              [9.7, 9.9, 2],
              [8.0, 8.3, 2],
              [6.3, 5.4, 1],
              [1.3, 2.7, 0],
              [2.3, 3.1, 0],
              [6.6, 6.0, 1],
              [6.5, 6.4, 1],
              [6.3, 5.8, 1],
              [9.5, 9.9, 2],
              [8.9, 8.9, 2],
              [8.7, 9.5, 2],
              [2.5, 3.8, 0],
              [2.0, 3.1, 0],
              [1.3, 1.3, 0]])
```

## Preparing the Data

We'll first put our data in a `DataFrame` table format, and assign the correct labels per column:


```python
import pandas as pd

df = pd.DataFrame(X, columns=['weight', 'length', 'label'])
df
```

`output`



|     | weight | length |  label |
| --- | ------:| ------:| -------:|
| 0   | 6.6 | 6.2 | 1.0 |
| 1   | 9.7 | 9.9 | 2.0 |
| 2   | 8.0 | 8.3 | 2.0 |
| 3   | 6.3 | 5.4 | 1.0 |
| 4   | 1.3 | 2.7 | 0.0 |
| 5   | 2.3 | 3.1 | 0.0 |
| 6   | 6.6 | 6.0 | 1.0 |
| 7   | 6.5 | 6.4 | 1.0 |
| 8   | 6.3 | 5.8 | 1.0 |
| 9   | 9.5 | 9.9 | 2.0 |
| 10  | 8.9 | 8.9 | 2.0 |
| 11  | 8.7 | 9.5 | 2.0 |
| 12  | 2.5 | 3.8 | 0.0 |
| 13  | 2.0 | 3.1 | 0.0 |
| 14  | 1.3 | 1.3 | 0.0 |

Now the data can be plotted to visualize the three different groups. They are subsetted by their label, assigned a different colour and label, and by repeating this they form different layers in the scatter plot.


```python
%matplotlib inline

ax = df[df['label'] == 0].plot.scatter(x='weight', y='length', c='blue', label='young')
ax = df[df['label'] == 1].plot.scatter(x='weight', y='length', c='orange', label='mid', ax=ax)
ax = df[df['label'] == 2].plot.scatter(x='weight', y='length', c='red', label='adult', ax=ax)
ax
```

`output`

![png](https://raw.githubusercontent.com/cmry/cmry.github.io/master/sources/output_6_1.png)


Looking at the plot above, we can see that the three classes are pretty well distinguishable by these two features that we have. Say that we apply $k$-NN to our data that will learn to classify new instances based on their distance to our known instances (and their labels). The algorithm needs a distance metric to determine which of the known instances are closest to the new one. Let's try to choose between either euclidean or cosine for this example.


## Picking our Metric

Considering instance #0, #1, and #4 to be our known instances, we assume that we don't know the label of #14. Plotting this will look as follows:


```python
df2 = pd.DataFrame([df.iloc[0], df.iloc[1], df.iloc[4]], columns=['weight', 'length', 'label'])
df3 = pd.DataFrame([df.iloc[14]], columns=['weight', 'length', 'label'])

ax = df2[df2['label'] == 0].plot.scatter(x='weight', y='length', c='blue', label='young')
ax = df2[df2['label'] == 1].plot.scatter(x='weight', y='length', c='orange', label='mid', ax=ax)
ax = df2[df2['label'] == 2].plot.scatter(x='weight', y='length', c='red', label='adult', ax=ax)
ax = df3.plot.scatter(x='weight', y='length', c='gray', label='?', ax=ax)
ax
```

`output`

![png2](https://raw.githubusercontent.com/cmry/cmry.github.io/master/sources/output_8_1.png)


### Euclidean

Our euclidean distance function can be defined as follows:

$\sqrt{\sum^n_{i=1} (x_i - y_i)^2}$

Where $x$ and $y$ are two vectors. Or:


```python
def euclidean_distance(x, y):   
    return np.sqrt(np.sum((x - y) ** 2))
```

Let's see this for all our vectors:


```python
x0 = X[0][:-1]
x1 = X[1][:-1]
x4 = X[5][:-1]
x14 = X[14][:-1]
print("x0:", x0, "\nx1:", x1, "\nx2:", x4, "\nx4:", x14)
```

`output`

    x0: [ 6.6  6.2]
    x1: [ 9.7  9.9]
    x2: [ 2.3  3.1]
    x4: [ 1.3  1.3]


Doing the calculations:

```python
print(" x14 and x0:", euclidean_distance(x14, x0), "\n",
      "x14 and x1:", euclidean_distance(x14, x1), "\n",
      "x14 and x4:", euclidean_distance(x14, x4))
```

`output`

     x14 and x0: 7.21803297305
     x14 and x1: 12.0216471417
     x14 and x4: 2.0591260282


According to cosine similarity, instance #14 is closest to #4. Our 4th instance had the label:


```python
X[4]
```

`output`



    array([ 1.3,  2.7,  0. ])



`0 = young`, which is what we would visually also deem the correct label for this instance.

Now let's see what happens when we use Cosine similarity.

### Cosine

Our cosine similarity function can be defined as follows:

$\frac{x \bullet y}{ \sqrt{x \bullet x} \sqrt{y \bullet y}}$

Where $x$ and $y$ are two vectors. Or:


```python
def cosine_similarity(x, y):
    return np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y)))
```

Let's see these calculations for all our vectors:


```python
print(" x14 and x0:", cosine_similarity(x14, x0), "\n",
      "x14 and x1:", cosine_similarity(x14, x1), "\n",
      "x14 and x4:", cosine_similarity(x14, x4))
```

`output`

     x14 and x0: 0.999512076087
     x14 and x1: 0.999947942424
     x14 and x4: 0.989203462354


According to cosine similarity, instance #14 is closest to #1. However, our 1st instance had the label:


```python
X[1]
```

`output`


    array([ 9.7,  9.9,  2. ])



`2 = adult`, which is definitely NOT what we would deem the correct label!

## So What Happened?

Consider the following picture:

![img](http://semanticvoid.com/images/cosine_similarity.png)

This is a visual representation of euclidean distance ($d$) and cosine similarity ($\theta$). While cosine looks at the **angle** between vectors (thus not taking into regard their weight or magnitude), euclidean distance is similar to using a ruler to actually measure the distance. In our example the angle between `x14` and `x4` was larger than those of the other vectors, even though they were further away.

## When to Use Cosine?

Cosine similarity is generally used as a metric for measuring distance when the magnitude of the vectors does not matter. This happens for example when working with text data represented by word counts. It is assumed that when a word (e.g. `science`) occurs more frequent in document 1 than it does in document 2, that document 1 is more related to the topic of `science`. However, it could be the case that we are working with documents of uneven lengths (Wikipedia articles for example). Then it might just be the case that `science` occurred more in document 1 because it was way longer than document 2. Cosine similarity corrects for this.

Text data is the most typical example for this metric. However, you might also want to apply cosine similarity for other cases where some properties of the instances make so that the weights might be larger without meaning anything different. Sensor values that were captured in various lengths (in time) between instances could be such an example.
