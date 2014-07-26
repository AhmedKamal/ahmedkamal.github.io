---
layout: post
title: How to get the Hijri Date in Windows 8.1 Accurately?
date: 2014-04-03 00:38
author: a7medkamal
comments: true
categories: [Hijri, Learn, non-Georgian-calendar, Programming, Windows 8.1, Windows 8.1]
---
I was trying to get the Hijri date while developing a windows 8.1 app but it wasn’t an easy task to do so especially when you know that unlike the normal .Net Framework , you can’t access Hirjri Calendar Class here although it is available due to MSDN documentation.

&nbsp;

To save your time , at first I used a simple web service that provides Hijri Date as a text and parsed it. The nice thing is that this service is provided by Al-Azhar (Dar Al-Iftaa) so it is credible and accurate and wouldn’t stop after a short time.

&nbsp;

I will share with you the code I wrote to get the date from this service
<div class="csharpcode">

[sourcecode language="csharp"]
            ConnectionProfile connection = NetworkInformation.GetInternetConnectionProfile();
            bool internet = connection != null &amp;&amp; connection.GetNetworkConnectivityLevel() == NetworkConnectivityLevel.InternetAccess;
            if (internet)
            {
                HttpClient client = new HttpClient();
                string res = await client.GetStringAsync(&quot;http://www.dar-alifta.org/dateservice.aspx?LangID=1&quot;);
                HtmlDocument doc = new HtmlDocument();
                doc.LoadHtml(res);

                DateTimeFormatter df = new DateTimeFormatter(&quot;longdate&quot;, new string[] { &quot;ar-sa&quot; });
                var date = df.Format(DateTime.Now);

                return doc.GetElementbyId(&quot;lblDate&quot;).InnerText;

            }
[/sourcecode]

</div>
<em><span style="color:#ff0000;">To parse the HTML result , I used HTML Agility Library.</span></em>

<span style="color:#333333;">Although the previous solution would be accurate , it still needs internet to get the result which would result in a problem if the user’s device isn’t connected to internet all time. So here is another way to get the date if there is no internet connection</span>

&nbsp;
<div class="csharpcode">

[sourcecode language="csharp"]
            DateTimeFormatter df = new DateTimeFormatter(&quot;longdate&quot;, new string[] { &quot;ar-sa&quot; });
            var date = df.Format(DateTime.Now);
            return date.ToString();
[/sourcecode]

</div>
Combining these two ways should satisfy your user who wants to be aware of the Hijri Date anytime.

&nbsp;

Regards ,

&nbsp;

Ahmed Kamal
