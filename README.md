# CircleCDN

_This README describes some fuzzy area between what the framework is _designed_ to do and what it _can do now_.  Both are moving targets, and subject to change.  Click [here]() for docs and a tutorial for using the application as it exists **today**_

CircleCDN is a full stack project to permit a web server to offload serving its resources to its clients.  The next time your site hits the top of hacker news, let your users take care of serving each other. 

This project is primarily intended as a big experiment to use a few fun new browser APIs. Because these tools are so new, cross browser support is... awful. For now, the project aims to support Chrome browsers only, with Firefox targeted soon after. (Note: a branch of this project is being built to support Firefox, but because the webrtc-datachannel apis are so new and so broken, the two will not be integrated for some time.)

## How it Works:

CircleCDN takes advantage of the new `WebRTC` system being developed by major browser vendors (with help from others).  `WebRTC` permits browsers to send and receive data straight to one another, without passing through any single server.  This is awesome.  

When a user visits a CircleCDN site, the server opens a WebSocket connection to that browser, and registers them as an available peer for others.  From then on, whenever a user requests some resource from the server, the server checks if it has already served it to an on-line peer.  If it finds someone with the resource, the server orders them to connect, and has the serving peer push the resource to its new friend. 

_(This configuration is quick for users, but more reliant on the server for resource coordination.  In the next version, users will first check with each other for the resource, and only seek it from the server if they can't find it independently.)_


## Server Side:

The server side code is written in [Tornado](http://www.tornadoweb.org/en/stable/), a Python async-server and web framework.  

Tornado is a ton of fun.  

### Server Side Flow:

The server exposes whatever static routes the user has chosen, as well as some dedicated signaling channel.  In practice the channel will almost definitely be a WebSocket (our client side library could easily be modified to use longpolling, but if your browser can't support WebSockets, then it can't support WebRTC, and you may as well be using a fax machine, or worse, IE6).  

As soon as a user hits some static route, they are assigned a unique userid, which will be used to coordinate serving resources to and from their browser.  Once the browser receives its first response, it will open a signaling channel to the server.  

Using this channel, the server will order the peer to connect to one of its peers.  Every peer will get two connections, one they serve to and one they get served by.  

From now on, any time the server needs some resource, it will ask its serving neighbor for that thing.  If that peer can satisfy that request, it responds with the resource, if not, it forwards the request down the line.  This goes on until someone can satisfy the request, or else until the originating user gets its own request, in which case it sends a new request to the server with a token indicating that the item is unavailable for peer-service.  


_In the near future, I hope to use the [Chord protocol](http://en.wikipedia.org/wiki/Chord_(peer-to-peer)) to improve the efficiency of this system._

### Server Side Libraries:


## Client Side:

_The client side uses no JavaScript libraries (not including ones I've written for this project), because why do something efficiently and painlessly when can just as easily cry yourself to sleep at night?  See?  Makes sense now._

### Client Side Flow:

The Client's application flow looks very similar to the Server's, except that it has to handle some rather more complicated routing.  

The WebRTC protocol is the fundamental tool underlying this program, so I'll briefly explain how the api works, before continuing on to explain my own code.

**WebRTC** is a giant pain in the ass.  It's also an **enormous** amount of fun.  The client establishes a signaling channel to the server so that it can get and receive WebRTC handshake messages from other peers.  The WebRTC teams at Google and Mozilla (and others) have done an insanely good job getting this protocol to work, but it's still a little tricky.  The approximate flow is as follows: 

1. browser creates a new PeerConnection object
2. browser creates a DataChannel object as an attribute to the PeerConnection (note, this is different than the signaling channel, they just seem to like the word 'channel'.  That's fine).
3. browser creates and sends an offer to connect to some remote user.  This message has to be sent through our server.
4. remote browser gets the connection offer, and responds with an answer object that's very similar to the offer, and the two send a barrage of messages to one another until they've reached a deal on how to connect.  
5. When the browsers are connected, the DataChannel mentioned above switches to 'open' state, and can send data over the wire, to its connected peer without ever touching the server again.  WHAT?? Yes. Seriously.  SO COOL!  I know.

Handling this process a single time isn't too difficult, but it can be tricky to coordinate connecting to multiple peers at once.  I've built a small library called [eventer.js](https://github.com/mbildner/CircleCDN/blob/master/static/javascript/eventer.js) to handle and react to incoming Signaling Channel messages, and to coordinate state for multiple peerconnections at once.  For now it works by calling methods out of a dispatch table (proving [Greenspun's tenth rule](http://en.wikipedia.org/wiki/Greenspun's_tenth_rule)), but I will eventually be porting it to work with [Custom Dom Events](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent).  Because Custom Dom Events are AWESOME.

The upshot of using eventer.js is that now the browser can create and use multiple peer to peer datachannels without a great deal of effort.  This forms the foundation of just about everything else this framework does.

Now that the user has an open channel to talk to its peer (and through that peer to all other peers), when it wants some resource, it simply asks the network if it has it stored on a client.  When a user requests some item, it adds an identifier for that thing to a list of outstanding requests, and waits to hear back.  Eventually, its serving neighbor will send it a message, which either will or will not satisfy that request.  If it does satisfy the request, the user registers that they have a copy of that piece of information, and removes it from their outstanding requests list.  If the user gets a reply from its serving peer that does not satisfy the request, then it fires a request to the server, which responds with the resource, which, as before, is now added to the user's list of available resources.

Since our goal is to have as much information available on each client (to maximize the odds that a request will be satisfied without touching the server), resources are stored in the browser's IndexedDB.  IndexedDB persists to disk, and provides fast, non-blocking reads, meaning that we don't have to flood the user's memory with a ton of useless objects which would either hog RAM or force a bunch of UI wrecking garbage collections.  It's a good thing :)

In the future, I plan to use Base64 encoding to encode and decode pictures for transmission between peers.  It is theoretically trivial, but I haven't done it yet, so for now we'll call it a "hard problem", so I can feel good about myself.  
