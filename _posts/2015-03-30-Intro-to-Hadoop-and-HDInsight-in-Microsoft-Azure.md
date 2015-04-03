---
layout: post
title: Intro to Hadoop and HDInsight in Microsoft Azure
date: 2015-03-30 17:00
author: Ahmed Kamal
comments: true
tags: [Hadoop ,BigData , Azure]
---

Hi, in this blog post, I will try to give you some info about Microsoft distribution of Hadoop. Hadoop is one of the most famous No Sql and big data solutions. Hadoop is now used by big entities like Facebook ,  Twitter , yahoo and many other companies that have a lot of data to store and process.
Let’s dive in a little deeper. If you don’t know what Hadoop is, let me give you one of the definitions that you can get easily from google :) 

> Hadoop is a free, Java-based programming framework that supports the
> processing of large data sets in a distributed computing environment

One of the scenarios when the usage of a technology like Hadoop is essential is when you have large amount of data that you want to analyze to get some information. 
For example, if you are working on a solution that tries to give your customer some information about people’s conversation about their companies in twitter. In this example, we have a large amount of data (tweet feeds) and at the same time you have to do a lot of processing (sentimental analysis) to be able to understand these tweets and decide if they are satisfied about the company or not. This would requires distributing this processing between multiple machines so that we could get the results in a reasonable amount of time.
Also In this example the data we are getting are unstructured that’s why storing them in a relational database won’t be useful and won’t help at all.

Back to Hadoop, the core of Apache Hadoop consists of two things:

1-	Storage Part which is called **HDFS** (Hadoop Distributed File System)

2-	Processing Part which is Map Reduce

> **MapReduce** is a programming model for processing and generating large data sets with a parallel, distributed algorithm on a cluster. A
> MapReduce program is composed of a Map() procedure that performs
> filtering and sorting (such as sorting students by first name into
> queues, one queue for each name) and a Reduce() procedure that
> performs a summary operation (such as counting the number of students  in each queue, yielding name frequencies).

To process the data, Hadoop Map/Reduce transfers code (specifically Jar files) to nodes that have the required data, which the nodes then process in parallel. 
There are multiple projects that can be used on top of Hadoop like:

**Mahout™**: A Scalable machine learning and data mining library.

**Hive™**: A data warehouse infrastructure that provides data summarization and ad hoc querying.

**Pig™**: A high-level data-flow language and execution framework for parallel computation.

**Spark™**: A fast and general compute engine for Hadoop data. Spark provides a simple and expressive programming model that supports a wide range of applications, including machine learning, stream processing, and graph computation.

**Storm™**: A free and open source distributed realtime computation system. Storm makes it easy to reliably process unbounded streams of data, doing for realtime processing what Hadoop did for batch processing.

and many other projects that are concerned with big data in general.

Microsoft has worked with Hortonworks (the creator of Hadoop) to deliver **HDInsight** which is provided through Azure or as on premise solution. HDInsight is a framework for the Microsoft Azure cloud implementation of Hadoop. It includes implementations of Storm, Pig, Hive, Sqoop and so on. 

HDInsight also integrates with business intelligence (BI) tools such as Excel, SQL Server Analysis Services, and SQL Server Reporting Services.

In the next blog posts , I will try to dive deeper into HDinsight in Azure. Thanks for reading :) Feel free to comment or contact me if you have any questions.

**References :**

http://en.wikipedia.org/wiki/Apache_Hadoop

http://en.wikipedia.org/wiki/MapReduce

http://hadoop.apache.org/

http://azure.microsoft.com/en-us/documentation/articles/hdinsight-hadoop-introduction/

