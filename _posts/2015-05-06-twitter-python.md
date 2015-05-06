---
layout: post
title: Syntactic Sugar for Tweepy
date: 2015-05-06 12:01:36
---

Lately I have been collection a large amount of tweets for building a good representation of the expected social discourse and its meta-data. After some digging around, I settled for [Tweepy](https://tweepy.readthedocs.org/) to interface with the Twitter API. There were several scenario's which I was looking to implement: grab the available associates (followers, friends) and timeline given a user's name, and resolving a large number of tweets given a set of tweet IDs. Don't get me wrong, Tweepy offers a very nice interface, but it was a bit too general-purpose for my liking, so I started building a wrapper class around Tweepy. In this post, I will talk a bit about its functionality, considerations and future improvements.

So, as a first, of course we start off initiating the class and setting some of the first local parameters. Please note that I will truncate the docstrings and only leave the parameters, the code is documented on github.


## Class __init__

{% highlight python %} 
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
{% endhighlight %}

## Profile-based methods

So starting for example `api = TwAPI('user')` already gives a fully authenticated api object to work with directly. Adding pieces of code to just retrieve friends and timelines isn't that big of a deal, we just call the appropriate Tweepy function:

{% highlight python %} 
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
{% endhighlight %}

Or if we want to do it in a generator, we edit this bit:

{% highlight python %} 
l = list()
for i in cursor.pages():
    for user in i:
        l.append(user.screen_name)
return l
{% endhighlight %}

To:

{% highlight python %} 
for i in cursor.pages():
    for user in i:
        yield user.screen_name
{% endhighlight %}

## Rate Limits

Either way, these functions do not have real added value, and we will quickly run into the [API rate limits](https://dev.twitter.com/rest/public/rate-limits). That's why I implemented a waiting function to correct for both processing time and amount of queries allowed per 15 minutes. The current version looks a bit horrible, but the general idea is as follows:

{% highlight python %} 
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
{% endhighlight %}

We can incorporate this into the existing functions as such:

{% highlight python %} 
def get_timeline(self, name):
    cursor = twp.Cursor(self.api.user_timeline, id=name, count=200)
    for i in cursor.pages():
        sleep(self.sleepy_time('timeline'))
        for tweet in i:
            yield tweet
{% endhighlight %}

## Stream and Geo

In order to pick Tweets from the stream, we need to add a bit more code. 

{% highlight python %} 
class StdOutListener(twp.StreamListener):

    def on_status(self, status):
        # do some stuff with the status
        return True

    def on_error(self, status_code):
        return True  # To continue listening

    def on_timeout(self):
        return True  # To continue listening

{% endhighlight %}

Adding this to our class:

{% highlight python %} 
def stream(self, bound_box):
    listener = StdOutListener()
    self.stream = twp.Stream(self.auth, listener)
    try:
        self.stream.filter(locations=bound_box)
    except Exception:
        print(traceback.format_exc())
{% endhighlight %}

If we include some database interaction in the `StdOutListener`, tweets can be directly fetched from the stream. Additionally, giving a `bound_box` of coordinates such as bb = [2.52490234375, 50.6976074219, 5.89248046875, 51.4911132813] allows us to only collect tweets in some area. Calling `api.stream(bb)` then continuously writes these out.

## List of id's

Close to every Twitter dataset offers either user or post id's that have to be resolved, as giving the entire status object is in violation of Twitter's terms of service. It is therefore likely that one has resolve these at some point. Twitter allows for feeding lists of 100 of such id's, which we can use in code as such:

{% highlight python %} 
def get_messages(self, msl):
    return self.api.statuses_lookup(msl, include_entities=True)

...
for 100_batch in batchlist:
	sleep(api.sleepy_time('messages'))
	msgl = api.get_messages(100_batch)
	for message in msgl:
		# do something
{% endhighlight %}

** To be updated **