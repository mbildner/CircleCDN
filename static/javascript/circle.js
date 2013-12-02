var PeerResourceRequest = function (targetPeerID, resourceID, callback) {
	var data;

	var request = {
		"SenderID" : userid,
		"RecipientID": targetPeerID,
		"Instructions" : {
			"Command" : 'resourceRequest',
			"Body" : resourceID
		}
	}

	var dataChannel = startRTCConnection(targetPeerID);

	var dataChannelListener = dataChannel.addEventListener('open', function (event) {
		var dataChannel = event.target;
		dataChannel.send(JSON.stringify(request));
	});

	var requestResponseListener = dataChannel.addEventListener('message', function (message) {
		var packet = JSON.parse(message.data);
		callback(packet.Instructions.Body);
	});

}



// cadence: 

// request resource
// get peer redirect Command
// request connection
// 		register onopen function to send data request
// on open send data request
// process request
// register with the server as a servable peer?