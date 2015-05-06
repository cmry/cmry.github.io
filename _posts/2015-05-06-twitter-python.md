---
layout: post
title: Syntactic Sugar for Tweepy
date: 2015-05-06 12:01:36
---

Lately I have been collection a large amount of tweets for building a good representation of the expected social discourse and its meta-data. After some digging around, I settled for [Tweepy](https://tweepy.readthedocs.org/) to interface with the Twitter API. There were several scenario's which I was looking to implement: grab the available associates (followers, friends) and timeline given a user's name, and resolving a large number of tweets given a set of tweet IDs. Don't get me wrong, Tweepy offers a very nice interface, but it was a bit too general-purpose for my liking, so I started building a wrapper class around Tweepy. In this post, I will talk a bit about its functionality, considerations and future improvements.

