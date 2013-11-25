import json
from random import choice

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options
from tornado import template



# -------------------------
# temporary code 
templates_path = "./"

loader = template.Loader(templates_path)





# -------------------------



def get_random_id(length):
	rand_char_string = "0123456789abcdefghijklmnopqrstuvwxyz"
	return "".join([choice(rand_char_string) for x in range(length)])



class Dispatcher(object):
	def __init__(self):
		self.websockets = {}

	def register_websocket(self, userid, websocket):
		self.websockets[userid] = websocket

	def unregister_websocket(self, userid):
		del self.websockets[userid]

	def route_message(self, message):
		self.websockets[json.loads(message)['RecipientID']].write_message(message)

		
		
class RTCmanager(object):
	def __init__(self, dispatcher):
		pass

	def connect_users(userid1, userid2):
		connection_message = {
			"SenderID" : "Server",
			"RecipientID" : useid1,
			"Instructions" : {
				"Command" : "startRTCConnection",
				"targetPeerID" : userid2
			}
		}

		message_payload = json.dumps(connection_message)

		return message_payload


# should the RTCmanager get a reference to the dispatcher or does that logic go in the route controller in Tornado?


dispatcher = Dispatcher()


class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.userid = self.get_cookie('userid')
		dispatcher.register_websocket(self.userid, self)

	def on_close(self):
		print 'connection closed'

	def on_message(self, message):
		dispatcher.route_message(message)


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.userid = self.get_cookie('userid')
		if not self.userid:
			self.userid = get_random_id(10)
			self.set_cookie('userid', self.userid)

		rendered_template = loader.load("tornado_template.html").generate(userid=self.userid)

		self.write(rendered_template)



application = tornado.web.Application([
    (r'/signalsocket', WSHandler),
    (r'/', MainHandler)
])
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)

    print "Tornado server starting."
    tornado.ioloop.IOLoop.instance().start()


 