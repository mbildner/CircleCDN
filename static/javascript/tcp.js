

var ReliableChannel = function (channel) {
	var channel = channel;

	var channelOpenListener = channel.addEventListener('open', function (event) {
		var channelOpenEvent = new CustomEvent('open', {"detail": {'channelOpen':true}});
		this.dispatchEvent(channelOpenEvent);
	});

	var newMessageListener = channel.addEventListener('message', handleMessage);

	var RebuiltMessage = function (index) {
		var index = index;
		var container = [];
		var addPiece = function (messagePiece) {
			var pieceIndex = messagePiece.index;
			var pieceInfo = messagePiece.info;
			container[pieceIndex] = pieceInfo;
			if (container.length >= index) {
				return container.join('');
			} else {
				return undefined;
			}
		}

		this.addPiece = addPiece;
		return this;		
	}

	var chunkMessage = function (data) {
		var chunkSize = 500;

		var chunks = [];
		var pieces = Math.ceil(data.length / chunkSize); 

		for (var i=0; i < pieces; i++) {
			var chunk = data.slice(i*chunkSize, (i+1) * chunkSize);
			chunks.push(chunk);
		}
		return chunks;
	}

	var messagePacker = function (recipient, index, message) {
		var pkg = {
			"SenderID" : userid,
			"RecipientID" : recipient,
			"Instructions" : {
				"Command" : "packedMessage",
				"Body" : {
					"index" : index,
					"info" : message
				}
			}
		}
		return JSON.stringify(pkg);
	}

	var send = function (recipient, message) {
		channel.send(messagePacker(recipient, 'START', message.length));
		chunkMessage(message).forEach(function (chunk, index) {
				channel.send(messagePacker(recipient, index, chunk));
			});
		channel.send(messagePacker(recipient, 'STOP', ''));
	}

	var messageHolder;
	var eventListenerHolder;

	var handleMessage = function (m) {
		var message = JSON.parse(m.data);

		if (message.Instructions.Command==='resourceRequest') {
			var dataset = localDataSets.retrieve(message.Instructions.Body);

			var response = {
				"SenderID": userid,
				"RecipientID" : message.SenderID,
				"Instructions" : {
					"Command" : 'resourceResponse',
					"Body" : dataset
				}
			}

			var responsePackage = JSON.stringify(response);

			send(responsePackage);

		} else if (message.Instructions.Command==='packedMessage') {
			receiveMessage(message);
		}
	}


	var receiveMessage = function (message) {
		var messagePiece = message.Instructions.Body;

		if (messagePiece.info==='START') {

			messageHolder = new RebuiltMessage(messagePiece.index);

		} else if (messagePiece.info==='STOP') {
			// do we need to mark the stop message?

		} else {
			var finishedMessage = messageHolder.addPiece(messagePiece);
			if (finishedMessage) {
				// someCallback(finishedMessage);
				console.log(finishedMessage);
			}
		}
	}

	this.close = channel.close;	
	this.send = send;

	return this;

}