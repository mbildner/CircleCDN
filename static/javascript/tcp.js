var data = JSON.stringify([1,2,3,4,5,6,7])

var chunked = function (data, pieces) {
	var chunkedData = [];
	var index = 0;
	var chunkSize = Math.ceil(data.length / pieces);
	for (var i=0; i < pieces; i++) {
		console.log(chunkSize);
		var chunk = data.slice(i*chunkSize, (i+1) * chunkSize);
		chunkedData.push(chunk);
	}
	return chunkedData;
}



var ReliableSender = function (channel) {
	var send = function (message) {

	}



}