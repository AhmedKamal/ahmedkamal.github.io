---
layout: post
title: Difference Between Class and Struct
date: 2012-10-23 15:43
author: a7medkamal
comments: true
categories: [C#, Class, Programming, programming, Struct]
---
I think many of who are learning Programming have confusion about the difference between "Class" and "Struct" concepts in C#.

One of the great explainations can be found in MSDN Library and in this post content depend on it .

Classes and structs are two of the basic constructs of the common type system in the .NET Framework. Each is essentially a data structure that encapsulates a set of data and behaviors that belong together as a logical unit. The data and behaviors are the members of the class or struct, and they include its methods, properties, and events, and so on, as listed later in this topic.

A class or struct declaration is like a blueprint that is used to create instances or objects at run time. If you define a class or struct called Person, Person is the name of the type. If you declare and initialize a variable p of type Person, p is said to be an object or instance of Person. Multiple instances of the same Person type can be created, and each instance can have different values in its properties and fields.

A class is a <span style="color:#ff0000;">reference type</span>. When an object of the class is created, the variable to which the object is assigned holds only a reference to that memory. When the object reference is assigned to a new variable, the new variable refers to the original object. <span style="color:#000080;">Changes made through one variable are reflected in the other variable because they both refer to the same data.</span>

A struct is a <span style="color:#ff0000;">value type</span>. When a struct is created, the variable to which the struct is assigned holds the struct's actual data. When the struct is assigned to a new variable, it is copied. The new variable and the original variable therefore contain two separate copies of the same data. <span style="color:#000080;">Changes made to one copy do not affect the other copy.</span>

In general, classes are used to model <span style="color:#ff0000;">more complex behavior</span>, or data that is intended to be modified after a class object is created. Structs are best suited for<span style="color:#ff0000;"> small data structures</span> that contain primarily data that is not intended to be modified after the struct is created.

&nbsp;

Best Wishes ,

Ahmed Kamal

&nbsp;
