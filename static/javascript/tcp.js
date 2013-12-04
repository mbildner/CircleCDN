var RebuiltMessage = function (index) {
	var index = index;
	var container = [];

	var addPiece = function (messagePiece) {
		var pieceIndex = messagePiece['index'];
		var messageInformation = messagePiece['info'];
		container[pieceIndex] = messageInformation;

		if (container.length===index) {
			return container.join('');
		}
	}

	this.addPiece = addPiece;

	return this;
}


var ReliableChannel = function (channel) {

	var channel = channel;

	var chunkSizer = function (data, maxSize) {
		// takes JSON
		var maxSize = maxSize || 500;
		return Math.ceil(data.length/maxSize);
	}

	var chunkMessage = function (data, chunkSize) {
		// takes JSON
		var chunkedData = [];
		var pieces = data.length / chunkSize;	

		
		for (var i=0; i < pieces; i++) {
			var chunk = data.slice(i*chunkSize, (i+1) * chunkSize);
			chunkedData.push(chunk);
		}
		return chunkedData;
	};

	var messagePacker = function (recipient, index, command, messagePiece) {
		var pkg = {
			"SenderID" : userid,
			"RecipientID" : recipient,
			"Instructions" : {
				"Command" : command,
				"Body" : {
					"index" : index,
					"messagePiece" : messagePiece
				}
			}
		}

		return JSON.stringify(pkg);
	}

	var send = function (recipient, message) {
		var chunked = chunkMessage(message, chunkSizer(message));
		var startMessage = messagePacker(recipient, chunked.length, "startMessage", "startMessage");

		channel.send(startMessage);
		chunked.forEach(function (messagePiece, index) {
			var messagePackage = messagePacker(recipient, index, "rebuildMessage", messagePiece);
			channel.send(messagePackage);
		});

		var stopMessage = messagePacker(recipient, -1, "stopMessage", "stopMessage");
		channel.send(stopMessage);

		console.log('chunked message send complete');
	};

	var messageHolder;

	channel.onmessage = function (m) {
		var message = JSON.parse(m.data);
	
		var command = message.Instructions.Command;
		var index = message.Instructions.Body.index;
		var messagePiece = message.Instructions.Body.messagePiece;

		if (command==="startMessage") {
			// there must be a better way to get container out of here, think it through in th
			messageHolder = new RebuiltMessage(index);
			console.log("new message starting");

		} else if (command==="rebuildMessage") {
			var readystate = messageHolder.addPiece(message);
			console.log(messagePiece);

			if (readystate) {
				console.log("finished with message");
				window.finishedmessage = readystate;
			}

		} else if (command==="stopMessage") {

			console.log("stop message received");

		} else {

			console.log("not sure: ");

		}

	};


	this.send = send;
	return this;
}