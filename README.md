# CircleCDN

CircleCDN is a full stack project to permit a web server to offload serving its resources to its clients.  The next time your site hits the top of hacker news, let your users take care of serving each other. 

This project is primarily intended as a big experiment to use a few fun new browser APIs.  Because these tools are so new, cross browser support is... awful.  For now, the project aims to support Chrome browsers only.  Firefox support will come soon.  (IE support is already here! just use a [Chrome frame](https://developers.google.com/chrome/chrome-frame/) to mitigate the suck!)


## How it Works:

CircleCDN takes advantage of the new `WebRTC` system being developed by major browser vendors (with help from others).  `WebRTC` permits browsers to send and receive data straight to one another, without passing through any single server.  This is awesome.  

When a user visits a CircleCDN site, the server opens a WebSocket connection to that browser, and registers them as an available peer for others.  From then on, whenever a user requests some resource from the server, the server checks if it has already served it to an on-line peer.  If it finds someone with the resource, the server orders them to connect, and has the serving peer push the resource to its new friend. 

_(This configuration is quick for users, but more reliant on the server for resource coordination.  In the next version, users will first check with each other for the resource, and only seek it from the server if they can't find it independently.)_



## Server Side:

The server side code is written in [Tornado](http://www.tornadoweb.org/en/stable/), a Python async-server and web framework.  


**MORE TO COME**