var usersList = document.getElementById('usersList');
		var connectUsersButton = document.getElementById('connectUsers');

		var websocket = new WebSocket("ws" + document.location.origin.substring(4) + "/" + "adminsocket");


		var connectUsers = function () {
			var userid1 = document.getElementById('userid1').value;
			var userid2 = document.getElementById('userid2').value;

			var connectUsersMessage = JSON.stringify({
				"SenderID" : "Admin",
				"RecipientID" : userid1,
				"Instructions" : {
					"Command" : "startRTCConnection",
					"Body" : userid2
				}
			});

			websocket.send(connectUsersMessage);		

		}


		var registerUser = function (userid) {
			var li = document.createElement('li');

			li.id = userid;

			var p = document.createElement('p');
			p.innerText = userid;

			li.appendChild(p);
			usersList.appendChild(li);

		}

		var unregisterUser = function (userid) {
			usersList.removeChild(document.getElementById(userid));
		}


		var wsOnOpen = function () {
			// pass
		}

		var wsOnClose = function () {
			// pass
		}

		var wsOnMessage = function (event) {
			var message = JSON.parse(event.data);

			if (message.command ==="register") {
				registerUser(message.userid);
			} else if (message.command === "unregister") {
				unregisterUser(message.userid);
			} else {
				console.log("unrecognized command");
			}

		}




		var wsOnOpen = websocket.addEventListener('open', wsOnOpen);
		var wsOnClose = websocket.addEventListener('close', wsOnClose);
		var wsOnMessage = websocket.addEventListener('message', wsOnMessage);
		var connectUsersHandler = connectUsersButton.addEventListener('click', connectUsers);
		var UIState = "unconnected";
		var UIStateMachine = {
		}
