---
layout: post
title: Lessons to learn from Parse about API design
date: 2015-05-16 17:00
author: Ahmed Kamal
comments: true
tags: [API,Software Design]
---
Recently, I have been concerned about best practices to follow while designing your software APIs.I'm working on a side project that requires designing an API that should hopefully be usable on different platforms so I asked myself why don't I try to learn from the best ?

By the best here I mean the guys on Google and Facebook. I planned to watch two session about best practices one needs to follow while designing an API. The one I watched and I'm going to discuss with you in this blog post is by the Kevin Lacker,  CTO of Parse , a company that provides BAAS (Backend as a service) solutions that is now part of Facebook.

First , if you aren't aware by what is the meaning of API.

> What is the meaning of API ? 
> API stands for "Application Programming Interface". 

APIs provide us with a great way to expose some of our programs and services to other people who can benefit from that while designing their apps. For example, instead of having to create your own authentication service, you can just use Facebook Authentication API. 
They simply did the hard task for you and you just have to write some boilerplate code before being able to get a robust authentication in few minutes!
Other examples indludes : Google Maps API , Twitter Streaming API , Yahoo Finance API , …. etc

Feel free to check this [link](https://www.pinterest.com/pin/481111172665337191/) for a smart infographic about APIs


APIs are sometimes called services or web services but web service is a broad concept that can represent  different things. The question that the session revolved around was **what are the best qualities that any grate API should have ?**

----------
#It should be intuitive
>  A good API needs to appeal to the most powerful emotion: Laziness - Kevin Lacker

 
It should be similar to what we know. For example, if its target users are .NET developers then they should feel that they are familiar to that API. This will happened if followed the same design guidelines and techniques that are famous in your target platform. 
####**a-	Similar things should look similar.**
For example, if we are providing the capability of exporting the text as PDF in two of our APIs components, the API user should be able to write exactly the same code in the two components and be able to get nearly the same result. 


####**b-	Dangerous things should be obvious**
At the same time, if you have some important and dangerous options that the API user  can change , the user should be aware of what is he going to do.

For example, imagine you have an API that is providing mobile developers with an easier way for data synchronization between their app and the server. If you have an option that will force the start of the download process from the beginning each time the connection is disconnected then you shouldn't just call it "SupportFreshDownload" no, in this case , you should choose a more terrifying name "CancelPreviousProgressWhenDisconnected". I hope you got the idea.


----------
#Well documented
> A bug in the code is worth two in the documentation.   -- unknown

Imagine, you have found a very cool API that would help you get the latest currency conversion prices easily and fast. It is also a free one! You tried to connect to it. You wrote some code, tried and tried but in vain. You can't get what you need so you decided you need some help. You tried to look here and there, to search for an official documentation but also you can't find something useful regarding it. 
I believe after all that time you spent without getting any initial results you would be frustrated and you would rather prefer to user another API that may be not free but with its powerful tutorials , support and documentation it saves you dozens of hours that you can invest in the development of the core of you application. This I guess was the reason why you have chosen to use an API at the first place.

####**a-	API Reference**
Simple questions should be simple to answer out of your docs. Think about what types of questions you want your docs to answer. 
You can also have an API reference docs. Some the languages like C# or Java have their platform specific reference (like Javadocs). Use them if there are ones. They would be boring of course but they should help anyone looking for some info about the function of this weird function that he has found.

####**b-	Tutorials**
Your tutorials should be fun, readable and self-contained so anyone could read one the tutorials and after that become able to apply what he learn easily without the need for a previous experience.

####**c-	QuickStart**
Quick start section should be very attractive and it should help you finish something in just couple of minutes. It should help you build a nice relationship with the API and encourages you to dig deeper.
I think you should check Parse [docs](https://parse.com/docs) especially the quickstart section



----------
#Opinionated
> You need to be opinionated even when there is no right and wrong - Kevin Lacker

While building your API , you can be hesitated about taking decisions. If there is a debate about something then you should take side from the the two. 
You API should be consistent within its different parts. 

You can't clone yourself of course so you should put rules so anyone who joins the development team could follow the same rule. If you intened to use a specific naming style then the others should follow this style. For example ,  If you decided that your response would be through JSON then all of your response should be compatible with JSON. API users should feel that the API is developed by one developer only :)


So that all I have for this post. I hope it could help you as I benefited from the talk. Feel free to watch [it](https://www.youtube.com/watch?v=qCdpTji8nxo) of course if you would like. If you have other things that you would like to share regarding the same topic , please do in the comments. If I had enough time , I would try to share with you what I have learnt from the other talk by one of Google's top engineers. Thanks a lot. 

