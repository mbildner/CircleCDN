var PeerResourceRequest = function (targetPeerID, resourceID, callback) {

	var request = {
		"SenderID" : userid,
		"RecipientID": targetPeerID,
		"Instructions" : {
			"Command" : 'resourceRequest',
			"Body" : resourceID
		}
	}

	// rename to reliableChannel
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