var PeerManager = function (userID, datachannel) {
	var userID = userID;
	var datachannel = datachannel;
	var peerID = undefined;


	var createPackageMessage = function (recipient, message) {
		var messagePackage = {
			"RecipientID" : recipient,
			"SenderID" : userID,
			"Instructions" : message 
		}
		return packageMessage;
	}


	var sendMessage = function (recipient, message) {
		var messagePackage = JSON.stringify(createPackageMessage(recipient, message));
		datachannel.send(messagePackage);
	}


	var consumeMessage = function (data) {
		// do stuff with the message
	}


	var processMessage = function (message) {
		var data = JSON.parse(message.data);

		var recipient = data.RecipientID;

		if recipient===userID {
			consumeMessage(data);

		} else if recipient==="Server" {
			// pass

		} else {
			sendMessage(recipient, data);
		}
	}


};