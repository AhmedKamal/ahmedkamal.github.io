---
layout: post
title: Do you know XAML ?
date: 2012-03-02 15:32
author: a7medkamal
comments: true
categories: [Windows Metro, Windows Phone]
---
<p style="text-align:center;"><img class="alignnone" src="http://i.zdnet.com/blogs/xamllogo.jpg" alt="" width="193" height="241" /></p>
Few months ago , I started to search about how one could program Metro Style Apps.
<blockquote><span style="color:#ff0000;">Metro Style Apps</span> <span style="color:#000080;">are new type of applications are available in Windows 8 inside Metro User Interface.</span></blockquote>
I knew that one can do that using  programming  language ( C# or VB.Net or C++) but  a markup language called<span style="color:#ff0000;"> XAML</span> is also needed. Perhaps it was the first time I heard about this new language. It is also needed if you want to program applications for Windows Phone 7 as well.
<blockquote><span style="color:#ff0000;">XAML</span>, ( <a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English">/</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English#Key">ˈ</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English#Key">z</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English#Key">æ</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English#Key">m</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English#Key">əl</a><a title="Wikipedia:IPA for English" href="http://en.wikipedia.org/wiki/Wikipedia:IPA_for_English">/</a>) is a <a title="Declarative programming" href="http://en.wikipedia.org/wiki/Declarative_programming">declarative</a> <a title="XML" href="http://en.wikipedia.org/wiki/XML">XML</a>-based language created by <a title="Microsoft" href="http://en.wikipedia.org/wiki/Microsoft">Microsoft</a> and is used for initializing structured values and objects.</blockquote>
For normal desktop applications XAML is used in a technology called WPF "<strong>Windows Presentation Foundation"</strong>
<blockquote>Due to Wikipedia defination <span style="color:#ff0000;">WPF</span>  is a <a title="Computer software" href="http://en.wikipedia.org/wiki/Computer_software">computer-software</a> <span style="color:#000080;">graphical subsystem for rendering user interfaces in Windows-based applications.</span></blockquote>
As applied to the .NET Framework programming model, XAML simplifies creating a UI for a .NET Framework application. You can create visible UI elements in the declarative XAML markup, and then separate the UI definition from the run-time logic by using code-behind files, this code is joined to the markup through partial class definitions.
<blockquote><span style="color:#0000ff;">namespace</span> WindowsPhoneApplication
{
<span style="color:#0000ff;">          public partial class</span> MainPage : PhoneApplicationPage
{
<span style="color:#99cc00;"> // Constructor</span>
<span style="color:#0000ff;">                            public</span> MainPage()
{
InitializeComponent();
}
}
}</blockquote>
XAML directly represents the instantiation of objects in a specific set of backing types defined in<span style="color:#0000ff;"> assemblies</span>.

<span style="color:#ff0000;">Note</span> : <span style="color:#333399;">This is unlike most other markup languages, which are typically an interpreted language without such a direct tie to a backing type system.</span>

XAML enables a workflow where separate parties can work on the UI and the logic of an application, using potentially different tools.

<span style="color:#ff0000;">Using <span style="color:#000000;">XAML we can create objects like buttons , Text boxes , Radio Buttons , ....etc</span></span>

For example to create a button we can do that through this code
<pre>&lt;Button Background="Blue" Foreground="Red" Content="This is a button"/&gt;</pre>
<h5><span style="color:#ff0000;"><strong>Foreground , Content <span style="color:#333399;">are properties of the object.</span></strong></span></h5>
<pre></pre>
