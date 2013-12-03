// extract the handlerDict and pass it into the eventer at construction time

var peerConnections = {};
var dataChannels = {};
var currentPeer;


// we need a consistent interface to handle the datachannel messages like we have for the websocket, for now abstract it to here and we can fix it later

var handlePeerMessage = function (m, dataChannel) {

	var message = JSON.parse(m.data);

	if (message.Instructions.Command==='resourceRequest') {
		var dataset = localDataSets.retrieve(message.Instructions.Body);

		var response = {
			"SenderID": userid,
			"RecipientID" : message.SenderID,
			"Instructions" : {
				"Command" : 'resourceResponse',
				"Body" : dataset.slice(0, 10)
			}
		}

		var responsePackage = JSON.stringify(response);
		dataChannel.send(responsePackage);

	} else if (message.Instructions.Command==='resourceResponse') {
		// var dataset = JSON.parse(message.Body);
		var dataset = message.Instructions.Body;
		// console.log(dataset);
	} else {
		// console.log(m);
	}

};



var breakRTCConnection = function (targetPeerID) {
	if (targetPeerID in peerConnections) {
		dataChannels[targetPeerID].close();
		delete dataChannels[targetPeerID];
		peerConnections[targetPeerID].close();
		delete peerConnections[targetPeerID];
		console.log('peer connection ' + targetPeerID + ' closed');
	} else {
		console.log("server ordered us to break RTC connection with " + targetPeerID + ", but no such connection exists");
	}
	return;
};


var localDescriptionCreated = function (description) {
	peerConnection.setLocalDescription(description);
	// TODO: a convenience function on eventer that uses an associated peer connection to auto-generate messages routed to the correct peer

	eventer.send(currentPeer, {
		"Command" : "handshake",
		"Body" : {
			"RemotePeerID" : userid,
			"sdp" : peerConnection.localDescription
		}
	});
}
var startRTCConnection = function (targetPeerID) {
		currentPeer = targetPeerID;
	// -----------------------------------
	// not sure where this code goes     
	// -----------------------------------
	var iceServers = {'iceServers': [{url: 'stun:stun.l.google.com:19302'}]};
	var optionalRtpDataChannels = { 'optional': [{'DtlsSrtpKeyAgreement': true}, {'RtpDataChannels': true }] };
	// -----------------------------------
	peerConnection = new webkitRTCPeerConnection(iceServers, optionalRtpDataChannels);
	peerConnections[targetPeerID] = peerConnection;
	var dataChannel = peerConnection.createDataChannel('RTCDataChannel', {reliable: false});

	var dataChannelOpenHandler = dataChannel.addEventListener('open', function (m) {
		dataChannels[targetPeerID] = this;
		console.log('datachannel open');

	});

	var dataChannelMessageHandler = dataChannel.addEventListener('message', function (m) {
		// pass in a reference to the datachannel so the callback can respond to sender.
		handlePeerMessage(m, this);
	});


	peerConnection.onicecandidate = function (candidate) {
		eventer.send(targetPeerID, {
			"Command" : "handshake",
			"Body" : {
				"RemotePeerID" : userid,
				"candidate" : candidate
			}
		});
	};

	peerConnection.createOffer(localDescriptionCreated, logErrors);

	// return the datachannel so we can add event listeners to it in the caller code
	return dataChannel;
};

// make my life easier, this should be moved somewhere else later
var logErrors = function (error) {
	console.log(error);
};



// eventer's signalling channel should be abstracted so that it can use longpolling etc
var ServerEventHandler = function (id, route) {
	var websocket = new WebSocket("ws" + document.location.origin.substring(4) + "/" + route);

	var handshakeManager = function (message) {

		var RemotePeerID = message.RemotePeerID;

		if (!(RemotePeerID in peerConnections)) {
			// we do not have a peerConnection counterpoint to this caller, make a new one and connect to him
			startRTCConnection(RemotePeerID);

		} else {
			// console.log("oh we've seen " + RemotePeerID + "before.");
		}

		var peerConnection = peerConnections[RemotePeerID];

		if (message.sdp) {
			var remoteSessionDescription = new RTCSessionDescription(message.sdp);
			// should this callback be defined elsewhere?
			var setRemoteDescriptionCallback = function () {
				if (peerConnection.remoteDescription.type==="offer") {
					peerConnection.createAnswer(localDescriptionCreated, logErrors);
				}
			}
			peerConnection.setRemoteDescription(remoteSessionDescription, setRemoteDescriptionCallback, logErrors);

		} else if (message.candidate.candidate) {
			var icecandidate = new RTCIceCandidate(message.candidate.candidate);
			peerConnection.addIceCandidate(icecandidate);
		} else {
			console.log("non sdp message");

		}


	}

	// command should be "channel"
	var wsEventsDict = {
		"alert" : function (message) {alert(message);},
		"log" : function (message) {console.log(message);},
		"startRTCConnection" : function (targetPeerID) {
			startRTCConnection(targetPeerID);
		},
		"breakRTCConnection" : function (targetPeerID) {
			breakRTCConnection(targetPeerID);
		},
		"handshake" : handshakeManager
	}

	var wsEventsHandler = function (event) {

		var Instructions = JSON.parse(event.data).Instructions;

		if (Instructions.Command in wsEventsDict) {
			wsEventsDict[Instructions.Command](Instructions.Body);
		} else {
			console.log(event.data);
			console.log(Instructions.Command + " is not a registered event");
		}
	}

	var websocketEventHandlers = websocket.addEventListener('message', wsEventsHandler);

	this.send = function (recipient, message) {
		var payload = {
			"SenderID" : userid,
			"RecipientID" : recipient,
			"Instructions" : message
		}
	websocket.send(JSON.stringify(payload));
	}
}
