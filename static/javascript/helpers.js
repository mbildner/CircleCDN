var addListItem = function (listElement, itemString) {
	var listItemNode = document.createElement('li');
	var listItemInformation = document.createElement('p');
	listItemInformation.innerText = itemString;
	listItemNode.appendChild(listItemInformation);
	listElement.appendChild(listItemNode);
}


var dictToParams = function (dict) {
	var params = [];
	for (var param in dict) {
		var key = param;
		var value = dict[param];
		var pair = key.toString() + '=' + value.toString();
		params.push(pair);
	}
	var paramString = "?" + params.join("&");
	return window.encodeURI(paramString);
}


var ajax = function (route, method, data, callback) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function () {
		if (xmlhttp.readyState===4 && xmlhttp.status===200) {
			callback(xmlhttp.responseText);
		}
	}
	if (method==="GET") {
		route = route + dictToParams(data);
	}
	xmlhttp.open(method, route, true);
	xmlhttp.send();
}





var clearElement = function (element) {
	while (element.children.length > 0) {
		element.removeChild(element.children[0]);
	}
}
