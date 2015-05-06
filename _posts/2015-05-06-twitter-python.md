---
layout: post
title: Syntactic Sugar for Tweepy
date: 2015-05-06 12:01:36
---

Lately I have been collection a large amount of tweets for building a good representation of the expected social discourse and its meta-data. After some digging around, I settled for [Tweepy](https://tweepy.readthedocs.org/) to interface with the Twitter API. There were several scenario's which I was looking to implement: grab the available associates (followers, friends) and timeline given a user's name, and resolving a large number of tweets given a set of tweet IDs. Don't get me wrong, Tweepy offers a very nice interface, but it was a bit too general-purpose for my liking, so I started building a wrapper class around Tweepy. In this post, I will talk a bit about its functionality, considerations and future improvements.

So, as a first, of course we start off initiating the class and setting some of the first local parameters. Please note that I will truncate the docstrings and only leave the parameters, the code is documented on github.


``` python
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

So starting for example `api = TwAPI('user')` already gives a fully authenticated api object to work with directly. Adding pieces of code to just retrieve friends and timelines isn't that big of a deal, we just call the appropriate Tweepy function:

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

Or if we want to do it in a generator, we edit this bit:

``` python
			for tweet in i:
                l.append(tweet)
        return l
```

To:

``` python
			for tweet in i:
                yield tweet
```