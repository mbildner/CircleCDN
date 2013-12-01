# CircleCDN

CircleCDN is a full stack project to permit a web server to offload serving its resources to its clients.  The next time your site hits the top of hacker news, let your users take care of serving each other. 

This project is primarily intended as a big experiment to use a few fun new browser APIs.  Because these tools are so new, cross browser support is... awful.  For now, the project aims to support Chrome browsers only.  Firefox support will come soon.  (IE support is already here! just use a [Chrome frame](https://developers.google.com/chrome/chrome-frame/) to mitigate the suck!)


## How it Works:

CircleCDN takes advantage of the new `WebRTC` system being developed by major browser vendors (with help from others).  `WebRTC` permits browsers to send and receive data straight to one another, without passing through any single server.  This is awesome.  

When a user visits a CircleCDN site, the server opens a WebSocket connection to that browser, and registers them as an available peer for others.  From then on, whenever a user requests some resource from the server, the server checks if it has already served it to an on-line peer.  If it finds someone with the resource, the server orders them to connect, and has the serving peer push the resource to its new friend. 

_(This configuration is quick for users, but more reliant on the server for resource coordination.  In the next version, users will first check with each other for the resource, and only seek it from the server if they can't find it independently.)_



## Server Side:

The server side code is written in [Tornado](http://www.tornadoweb.org/en/stable/), a Python async-server and web framework.  

Tornado is a ton of fun.  

The server exposes a WebSocket route for clients to connect to, as well as a few regular static urls.  The application flow is as follows:

1.  ### User hits the site
	When a user first hits the site, their browser is assigned a unique identifier string, and the server establishes a signaling channel to that browser, identified by its userid.  

2. ### Server establishes signaling channel with user

	The signaling channel is used to request and coordinate the creation of peer to peer connections between this user and others.  

	_(see [here](http://www.html5rocks.com/en/tutorials/webrtc/infrastructure/) for more information on the idea behind signaling channels.)_ [1]


3. ### User is connected to the peer mesh [2]



### The Managing Classes:



## Client Side:



**MORE TO COME**

[1]: As of now, the signaling channel defaults to a WebSocket, for ease of development.  Our javascript library [eventer.js](https://github.com/mbildner/CircleCDN/blob/master/static/javascript/eventer.js) is designed to permit a quick swap-in of long polling or some other (hacky) bidirectional communication link as desired.  It would of course be crazy to try to use WebRTC with a browser that can't support WebSockets. But... who knows.

[2]: Mesh