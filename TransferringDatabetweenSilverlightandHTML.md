In the last few years, html and JavaScript became one of the most used technologies and a lot of applications are now being rewritten in them because of the known multiple benefits of them. At the same time, Silverlight was one of the promising technologies few years ago especially for .Net developers and thus many big applications are already written in it.  In this blog I will try to discuss how Silverlight can communicate with HTML pages and vice versa. 

First, there are two main techniques to show html pages inside Silverlight applications. 
1-	Web Browser Control
2-	Using Iframe element

> Note : An IFrame (Inline Frame) is an HTML document embedded inside
> another HTML document on a website. The IFrame HTML element is often
> used to show content from another source, such as an advertisement,
> into a Web page.

You can also check [Dan Whalen](http://weblogs.asp.net/dwahlin/integrating-html-into-silverlight-applications) blog post for further details about these options. In this post I will choose the second option because of its simplicity and backward compatibility.

The challenge now is to make this html page that appears inside the iframe able to invoke specific action that affects the Silverlight application and to make Silverlight able to control the html page too.
Before explaining how to do so, I ‘d like to remind you that Silverlight is hosted inside an asp.net application and so our asp.net page like any web application can contain JavaScript code. Through this JavaScript code, we can invoke any scriptable C# methods.
To make our C# code ready to be invoked by javascript , we need to 

1-	Create a class containing all our methods such that each method has **[ScriptableMember]** attribute above it.

2-	Register an instance of this class in app.xaml.cs file inside Application_Startup method to guarantee that it will be registered when the Silverlight app starts.

ScriptableMethods scriptMethods = new ScriptableMethods();
HtmlPage.RegisterScriptableObject("SL2JS", scriptMethods);
Let’s say we need to expose a method called GetMyMagicalSecret() , this method would be called by Javascript code 

   

     public class ScriptableMethods{
    
            [ScriptableMember]
            public void GetMyMagicalSecret (int index){
            if(index == -1) 
                ShowText("-1 isn’t a good place for secrets");
            else ShowText("Work Smarter Not Harder");
            
            }
    
            public void ShowText(string text){
            //Some Code
            }
        }

In the default.aspx file we will notice few things :
1-	Our Silverlight control is hosted in a div inside HTML which is passed the XAP file of our Silverlight application.
2-	There are few parameters inside the Silverlight object that can be configured. One of the parameters is “OnLoad” which will be attached to a javascript method 

      <param name="onLoad" value="pluginLoaded" />

This event is fired when the application is fully loaded.

    function pluginLoaded(sender, args) {
                  slCtrl = sender.getHost();
              }

This way we will have a variable through which we can control our Silverlight application
If we want for example to know my magical secret , you should call it this way 
slCtrl.Content.SL2JS.GetMyMagicalSecret(1);

> Don’t forget that SL2JS is our instance of ScriptableMethods class
> that was created inside our app.xaml.cs file.

Ok , so now we can need to do the reverse which is calling JavaScript code from Silverlight. This can be achieved through a method called invoke. Example :
Html.Window.Invoke(“MethodName” , params);

> Params can be multiple variables not just one.

**Question:** In all these examples, we used JavaScript that exists in the aspx file. What if we want for example to depend on JavaScript code that exists inside our frame?
I guess it would be better to answer it in a new blog post :) 

Thanks for your time. If you have any other ideas / suggested solutions or feedback, please let me know through comments.

