---
title: The Twitter API and Python - Syntactic Sugar for Tweepy
date: 2015-05-08 14:19:36
---

Lately I have been collecting a large amount of tweets for building a good representation of Twitter-user's expected social discourse and its meta-data. Basically, a fancy way of saying that I want to see who *publicly* shares what, and with whom. After some digging around, I settled for [Tweepy](https://tweepy.readthedocs.org/) to interface with the Twitter API. There were several scenarios which I was looking to implement: grab the available associates (followers, friends) and public timeline given a user's name, and resolving a large number of tweets given a set of tweet IDs. Don't get me wrong, Tweepy offers a very nice interface. It was a bit too general-purpose for my liking though, so I started building a wrapper class around Tweepy. In this post, I will talk a bit about its functionality, considerations and future improvements while discussing the task of utilizing the Twitter API for Natural Language Processing-related research.

![twitter](http://www.dototot.com/wp-content/uploads/2013/11/guidoTwitterBot_final1-1.jpg)

## Introduction

Twitter's short messaging system has been a well known hurdle for many tasks related to Natural Language Processing (NLP). Most of the techniques in its field tend to work very well given enough context per document; something which is clearly constrained in tweets. It therefore makes for a very challenging and equally interesting platform to work with. Accessing its data, however, can prove a time consuming task. To illustrate: if you're interested in a specific topic relevant for only a region or language (such as political tweets), you can either hope to get some share of this in its [stream](https://dev.twitter.com/streaming/overview), or constrain it with geo location (which many people do not enable). Keeping in mind that a [normal human being](https://www.quora.com/How-much-does-access-to-the-Twitter-firehose-cost?share=1) only has access to a very small percentage of this stream makes it all the more annoying at times. One might think: well, if I know a person who's from the country I'm interested in, I can just pull his tweets and look at those of his friends as well, right? Turns out it's not that simple.

# The Twitter API & Tweepy

Twitter offers an interface to the tasks I described above, as well as a wide variety of most other information one would like to get his hands on. These can in essence be accessed through a [REST](#) interface, which might be rather unintuitive to novel users. Luckily most programming languages offer a wrapper for this API, [Tweepy](https://tweepy.readthedocs.org/) for Python being one of them. To access the API, you need a Twitter account and developer credentials - the latter of which can be obtained by creating an 'app', for which one can refer to [apps section](https://apps.twitter.com/). After receiving your brand spanking new app environment, it will list a *manage keys and access tokens* point near the Consumer Key. From that section, you can generate the tokens needed to fill in for authorization, which I will refer to as `cons_key`, `cons_sec`, `accs_tok`, `accs_sec`. There are two steps to this authorization; app-level authorization, and-user level authorization. The `cons_` keys are needed for app-level, and need to be combined with the `accs_` ones for user-level authorization. This will give us app-level:

``` python
import tweepy

cons_key = 'XXXXXXXXXXXXXXXXX' # own key
cons_sec = 'XXXXXXXXXXXXXXXXX' # own key

auth = tweepy.AppAuthHandler(cons_key, cons_sec)
```

While this is needed for user-level:

``` python
cons_key = 'XXXXXXXXXXXXXXXXX' # own key
cons_sec = 'XXXXXXXXXXXXXXXXX' # own key
accs_tok = 'XXXXXXXXXXXXX' # own key
accs_sec = 'XXXXXXXXXXXXX' # own key

auth = tweepy.OAuthHandler(cons_key, cons_sec)
auth.set_access_token(accs_tok, accs_sec)
```

Notice that the latter has a different Handler, and needs to add the tokens after creating the `auth` variable. If no errors are thrown, you are good to go! Given that we authenticated ourselves, we can now move the `auth` variable in the API, and do something such as:

``` python
api = tweepy.API(auth)
api.friends('username')
```

Which will return up until some amount of friend-names in a list! Great! Now that wasn't so hard, right? Not yet.

# Twitter Rate Limits & Pagination

Well, turns out Twitter has long monetized its data access, and therefore only allows you to pull this `api.friends` for different accounts only some X amount of times per 15 minutes. These rate limits vary per access level (user/app), which is acceptably well documented [here](https://dev.twitter.com/rest/public/rate-limiting) (Twitter docs can be incredibly vague). On top of that, the amount of entries that can be retrieved per 'page' also varies. Example: say that we want to list all the friends from some guy or girl who has more than 200 friends. Twitter only allows us to access these in pages of 200 friends. So in the previous example where I just called `api.friends('username')` we would get 200 friends only, even if the person has more. To solve this, we need to use a `Cursor` function, which in Python is similar to a [generator](). You can call its `pages()` for iteration, which works as follows:

``` python
cursor = tweepy.Cursor(api.friends, id=name, count=200)
for page in cursor.pages():
    for friend in page:
        # do something with a friend
```

Each time we access the API, regardless of doing this in `cursor.pages()` or without, Twitter will count it as one access instance. Per access instance, Twitter substracts one from the rate limit counter. These rate limits can be viewed with `api.rate_limit_status()`, which returns a dict listing, amongst others, remaining queries per function. So if we look this up for the query we previously used, we see:

``` python
In [4]: api.rate_limit_status()['resources']['friends']
Out[4]:
{'/friends/following/ids': {'limit': 15, 'remaining': 15, ...},
 '/friends/following/list': {'limit': 15,
  'remaining': 15,
  'reset': 1430993361},
 '/friends/ids': {'limit': 15, 'remaining': 15, 'reset': 1430993361},
 '/friends/list': {'limit': 30, 'remaining': 29, 'reset': 1430993361}}
```

Note that at '/friends/list' we can only query 30 times as an authenticated app, and we queried once, so we have 29 remaining. These rate limits reset once every 15 minutes - the 'reset' counter keeps track of how much time remains until this renews (in [~~Epoch~~ Unix time](https://en.wikipedia.org/wiki/Unix_time)). Therefore, the optimal interval $i = 15 \cdot 60 / lim$, where $lim$ is the limit. With this, we can define the time it will take to process a query ($t(q)$), by incorporating the number of results $max$ we can get per `Cursor`, and the total instances $sum$. As such:

\begin{equation}
t(q) = \frac{sum}{max} \cdot i = \frac{sum}{max} \cdot \frac{15 \cdot 60}{lim}
\end{equation}

So say that we have three profiles with 1000 ($max = 1000 \cdot 3$) friends, this would result in $t(q) = 3000 / 200 \cdot 15\cdot60 / 30 = 450$ seconds (!) for three profiles. This isn't such a big deal when we're only interested in a fairly small amount of people. Otherwise we'll have to sit this query process out for a while, which definitely needs to be taken into account whilst designing an experimental setup.

When writing a program that uses this API and which has to deal with its rate limits, it would be a good thing to optimize the amount of queries per some amount of seconds, especially when database interactions, preprocessing and this kind of stuff is happening in the background and taking up time before the next query. This was one of the reasons I started developing the wrapper for Tweepy; to make sure that the $t(q)$ in our equation is very approximate to the amount of time the class methods will be taking.

## Syntactic Sugar

As you might know, syntactic sugar is a way to describe syntax in a programming language that makes it 'tastier to consume': easier to read, work with, or just to make things work in an alternative style. Now while this is predominantly used for lower-level code, it also works well to describe a  type of wrapper. The aim is then to simplify certain interactions, that do mostly the same as existing code, but in a more intuitive or task-specific manner (of which the latter is the case here). So, let's get into the design now.

# Class __init__

We start off initiating the class, of course, and setting some of the first local parameters. Please note that I will truncate the docstrings and only leave the parameters, the code is documented on [github](). Moving the `auth` function to be called by either 'user' or 'app' makes fiddling with the different handler classes a little less troublesome. Now starting for example `api = TwAPI('user')` already gives a fully authenticated api object to work with directly!

``` python
import tweepy as twp

class TwAPI:

	def __init__(self, mode):
        """
        :mode: either "user" or "app"
        :return: nothing
        """

        cons_key = 'XXXXXXXXXXXXXXXXX' # own key
        cons_sec = 'XXXXXXXXXXXXXXXXX' # own key

        if mode == "user":
            accs_tok = 'XXXXXXXXXXXXX' # own key
            accs_sec = 'XXXXXXXXXXXXX' # own key

            self.auth = twp.OAuthHandler(cons_key, cons_sec)
            self.auth.set_access_token(accs_tok, accs_sec)

        if mode == "app":
            self.auth = twp.AppAuthHandler(cons_key, cons_sec)

        self.mode = mode
        self.api = twp.API(self.auth)
```

> **Note:** For future work, it is probably a good idea to move the tokens a bit higher level in the code (like in a dict) so you don't have to fiddle inside the class. Might also be better to make TwAPI an api class, so you can just call `self.user_timeline` instead of `self.api.user_timeline`.

# Profile-based methods

Adding pieces of code to just retrieve friends and timelines isn't that big of a deal, as we saw before. We integrate the cursor part and the iterator in separate methods and we just call the appropriate Tweepy function:

``` python
def get_friends(self, name):
    cursor = twp.Cursor(self.api.friends, id=name, count=200)
    l = list()
    for i in cursor.pages():
        for user in i:
            l.append(user.screen_name)
        return l

def get_timeline(self, name):
    cursor = twp.Cursor(self.api.user_timeline, id=name, count=200)
    l = list()
        for tweet in i:
            l.append(tweet)
        return l
```

Both of these functions have a preset maximum count window, and store all the retrieved data in one list, and return that. Due to memory constrains on big sets, it could be better to do it in a generator. For this, we edit this bit:

``` python
- l = list()
  for i in cursor.pages():
      for user in i:
+         yield user.screen_name
-         l.append(user.screen_name)
- return l
```

Then we interact with these class methods like so:

``` python
In [1]: api = TwAPI('user')

In [2]: api.get_friends('_cmry')
Out[2]:
['ProjectJupyter',
...
```

Note that this assumes that you want pagination anyway; there is no real reason to call the method without a cursor. In normal code, it is just a tad neater to omit this if you do not need multiple pages. This implies, however, that it will **always** retrieve the entire object. If you decide that someone with 1000 friends has only a relevant slice of the first or last 200, then it's best to alter the code. Moreover, though the methods have very similar functionality their 'pre-sets' (`count`, field calls) make it so that abstraction was avoided on purpose.


# Handling Rate Limits

Either way, these functions do not have real added value as-is, and we will quickly run into the [API rate limits](https://dev.twitter.com/rest/public/rate-limits) as we have them set up now. That's why I implemented a waiting function to correct for both processing time and amount of queries allowed per 15 minutes. The current version looks a bit horrible, but the general idea is as follows:

``` python
from time import sleep, strftime, time

TIME = time()

...

def sleepy_time(self, sw):
    """
    TODO: make the limit fetch itself given a target so we can get
          rid of the ugly if/elif statements that do the same. Can
          be fetched from self.api.rate_limit_status()['resources'].

    :sw: friends or messages
    :return: float cooldown seconds
    """
    global TIME
    t = strftime('%H:%M:%S')
    if sw == 'friends':
        lim = 0  # correct
    elif sw == 'messages':
        lim = 180 if self.mode == "user" else 60
    elif sw == 'timeline':
        lim = 180 if self.mode == "user" else 300
    else:
    	lim = 15 if self.mode == "user" else 30

    process_time = time() - TIME
    TIME = time()
    cooldown = float(15 * 60) / float(lim) - process_time

    return cooldown if cooldown > 0 else 0
```

We can incorporate this into the existing functions as such:

``` python
def get_timeline(self, name):
    cursor = twp.Cursor(self.api.user_timeline, id=name, count=200)
    for i in cursor.pages():
        sleep(self.sleepy_time('timeline'))
        for tweet in i:
            yield tweet
```

Using these functions between each iteration, the hope is to approximate $t(q)$ as defined before. To properly correct for computation time between functions, the method tries to see how much global time has passed since the previous call, however, if this is $-$, the current code does not smear that out across multiple iterations. This is something for future work.

# Stream and Geo

Previously I talked about the possibility for one to interact with the Twitter stream. Here, you can 'attach' yourself to the entire live stream of messages that are sent over Twitter. Despite the fact that you can only see some very small percentage of the actual data, sometimes it's useful to use in combination with a filter. The stream allows keyword filtering, as well as geo filtering. In the first case, we tell twitter that if there's a certain keyword (for example 'semantic'), we want it to show up in our stream. In Python, this would look something like this:

``` python

11:49:41 - (stream): filtering keyword 'semantic'
11:49:42 - (stream): cravetrain: Semantic timeline markup, hCal ...
11:54:07 - (stream): djplb: @rustuswayne Obama!s Groundbreaking ...

```

If we visualize:

![stream](http://www.digital-constructions.com/blog/uploaded_images/twitterStreamGraph-799455.jpg)

In order to pick these Tweets from the stream, we need to add a bit more code. First off, there needs to be a `StdOutListener` so that whatever is given to the streamer can actually be handled in Python:

``` python
class StdOutListener(twp.StreamListener):

    def on_status(self, status):
        print(status['text'])
        # do some stuff with the status
        return True

    def on_error(self, status_code):
        return True  # To continue listening

    def on_timeout(self):
        return True  # To continue listening

```

Replacing `# do some stuff...` with database or file interactions allows direct storing of any [Status Object](https://dev.twitter.com/rest/reference/post/statuses/update) that the stream yields. To check if we're doing fine, I wrote a small print for `status['text']` here. Now that we have this, we can go about writing the method to call the stream. We add this to the `TwAPI` class:

``` python
def stream(self, o_filter):
    listener = StdOutListener()
    self.stream = twp.Stream(self.auth, listener)
    try:
        if type(o_filter) == list():
            self.stream.filter(locations=o_filter)
        else:
            self.stream.filter(o_filter)
    except Exception:
        print(traceback.format_exc())
```

As can be seen, we can give this method some filter; either a `str` or a `list`. The list functions as a bound box for coordinates, such as bb = [2.52490234375, 50.6976074219, 5.89248046875, 51.4911132813]  (for Belgium). This will allow you to only collect tweets in some area. Alternatively, passing a string results in the keyword filter I discussed. Sadly, due to the fact that stream only allows you to view a small percentage of the actual data, the more specific your searches will be, the less frequent things will show up in the stream.

# Twitter datasets & List of IDs

Luckily, we can avoid working with most of the heavy rate limits by using Twitter datasets. These datasets are usually constructed for research purposes; therefore, if you're in luck they will have some form of annotation that provides more meta-data on instance. For example, one might receive a list of user IDs and an annotated gender. Close to every Twitter dataset offers either these user or tweet IDs that have to be resolved, as giving the entire status object is in violation of Twitter's terms of service. It is therefore likely that one has to retrieve either the User or Status objects at some point. Twitter allows for feeding lists of 100 of such IDs, which we can use in code as such:

``` python
def get_messages(self, msl):
    return self.api.statuses_lookup(msl, include_entities=True)

...
for 100_batch in batchlist:
	sleep(api.sleepy_time('messages'))
	msgl = api.get_messages(100_batch)
	for message in msgl:
		# do something
```

This would start resolving the ID's, after which they can be written do a database, file, or whatever. The advantage here is that at times you are able to process tweets much faster; say that we have 100.000 messages, then $t(q) = 100.000 / 100 \cdot 15\cdot60 / 180 = 5000$ seconds. In comparison with for example the user timeline where we would need to retrieve around 30 profiles for the same amount of messages, then $t(q) = 100.000 / 200 \cdot 15 \cdot 60 / 300 = 1500$ seconds only, this is slower. However, seeing that we already know what we are looking for (each tweet is relevant to our research), and that we still process 20 tweets per second, this is a good trade-off to make in specific cases.
