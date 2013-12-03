var ReliableSender = function (channel) {

	var chunkMessage = function (data, pieces) {
		var chunkedData = [];
		var index = 0;
		var chunkSize = Math.ceil(data.length / pieces);
		for (var i=0; i < pieces; i++) {
			var chunk = data.slice(i*chunkSize, (i+1) * chunkSize);
			chunkedData.push(chunk);
		}
		return chunkedData;
	};



	var send = function (message) {
		var chunked = chunkMessage(message, 5);
		console.log(chunked);
	};


	var processMessage = function (message) {
		console.log(message);
	};




	this.send = send;

	return this;

}