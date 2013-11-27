import json
from random import choice

def get_random_id(length):
	rand_char_string = "0123456789abcdefghijklmnopqrstuvwxyz"
	return "".join([choice(rand_char_string) for x in range(length)])




class Master(object):
	def __init__(self, dispatcher, peerconnectionsmanager, datamanager):
		self.dispatcher = dispatcher
		self.datamanager = datamanager
		self.peerconnectionsmanager = peerconnectionsmanager

	def handle_message(self, message):
		recipient = json.loads(message)['RecipientID']
		if recipient=="Server":
			pass
		else:
			self.dispatcher.route(message, recipient)

	def register_peer(self, userid):
		self.peerconnectionsmanager.register_peer(userid)

	def register_websocket(self, userid, websocket):
		self.dispatcher.register_websocket(userid, websocket)

	def unregister_websocket(self, userid):
		self.dispatcher.unregister_websocket(userid)





class Dispatcher(object):
	def __init__(self):
		self.websockets = {}

	def register_websocket(self, userid, websocket):
		self.websockets[userid] = websocket

	def unregister_websocket(self, userid):
		self.websockets.pop(userid)

	def route(self, message, recipient):
		self.websockets[recipient].write_message(message)




class DataManager(object):
	def __init__(self):
		self.data_registry = {}

	# does register_dataset get a reference to the actual dataset too?
	def register_dataset(self, dataset_id):
		self.data_registry[dataset_id] = self.data_registry.get(dataset_id, [])

	def unregister_dataset(self, dataset_id):
		self.data_registry.pop(dataset_id) 

	def remove_serving_peer(self, dataset_id, peer):
		self.data_registry[dataset_id].remove(peer)

	def get_serving_peers(self, dataset_id):
		return self.data_registry.get(dataset_id, [])




class PeerConnectionManager(object):
	def __init__(self):
		self.peers = {}
		self.peer_connections = []

	def register_peer(self, userid):
		self.peers[userid] = self.peers.get(userid, [])

	def unregister_peer(self, userid):
		self.peers.pop(userid)
		for peer_list in self.peers.values():
			peer_list.remove(userid)






	# def register_peer_connection(self, userid1, userid2):
	# 	pass

	# # who is responsible for managing peer connections?
	# def connect_users(self, userid1, userid2):
	# 	connection_message = {
	# 		"SenderID" : "Server",
	# 		"RecipientID" : userid1,
	# 		"Instructions" : {
	# 			"Command" : "startRTCConnection",
	# 			"targetPeerID" : userid2
	# 		}
	# 	}

	# 	message_payload = json.dumps(connection_message)
	# 	return message_payload


	# def disconnect_users(self, userid1, userid2):
	# 	pass


