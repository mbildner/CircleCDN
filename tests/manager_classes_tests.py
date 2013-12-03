import unittest
import random


from webrtc.RTCManager import get_random_id
from webrtc.RTCManager import Dispatcher



class MockedWebSocket(object):
	def __init__(self):
		self.readystate = False
		self.messages = []
		
	def write_message(self, message):
		self.messages.append(message)

	def close(self):
		seld.readystate = False

	def open(self):
		self.readystate = True


def prepped_websocket():
	ws = MockedWebSocket()
	ws.open = True
	return ws





class DispatcherTests(unittest.TestCase):

    def setUp(self):
    	self.dispatcher = Dispatcher()

    def test_register_websocket(self):
    	userid = get_random_id(10)
    	websocket = prepped_websocket()

    	self.dispatcher.register_websocket(userid, websocket)
    	self.assertEqual(len(self.dispatcher.websockets), 1)

    def test_unregister_websocket(self):
    	userid = get_random_id(10)
    	websocket = prepped_websocket()

    	self.dispatcher.register_websocket(userid, websocket)
    	self.dispatcher.unregister_websocket(userid)
    	self.assertEqual(len(self.dispatcher.websockets), 0)


    def test_route(self):
    	websockets = {get_random_id(10):prepped_websocket() for x in range(10)}

    	for userid, websocket in websockets.items():
    		self.dispatcher.register_websocket(userid, websocket)

    	sender = random.choice(websockets.keys())
    	recipient = random.choice(websockets.keys())

    	mocked_message = {
    		"SenderID" : sender,
    		"RecipientID" : recipient,
    		"Instructions" : {
    			"Command" : "startRTCConnection",
    			"Body" : recipient
    		}
    	}

    	self.dispatcher.route(mocked_message, recipient)

    	self.assertTrue(mocked_message in websockets[recipient].messages)


class MasterTests(unittest.TestCase):

	def setUp(self):
		pass






    # def test_thing(self):
    # 	self.assertTrue(True)

    # def test_otherthing(self):
    # 	self.assertEqual(1,1)









if __name__ == '__main__':
    unittest.main()

