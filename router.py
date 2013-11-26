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

	def route(self, message):
		recipient = json.loads(message)['RecipientID']
		self.websockets[recipient].write_message(message)



class RTCmanager(object):
	def __init__(self):
		pass

	def connect_users(self, userid1, userid2):
		connection_message = {
			"SenderID" : "Server",
			"RecipientID" : userid1,
			"Instructions" : {
				"Command" : "startRTCConnection",
				"targetPeerID" : userid2
			}
		}

		message_payload = json.dumps(connection_message)

		return message_payload


# should the RTCmanager get a reference to the dispatcher or does that logic go in the route controller in Tornado?





admin = None

dispatcher = Dispatcher()
rtcmanager = RTCmanager()

# should admin method calls be placed inside the dispatcher class?
class SignalSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.userid = self.get_cookie('userid')
		dispatcher.register_websocket(self.userid, self)

		# tell admin we have a new user
		admin.write_message(json.dumps({"command":"register", "userid":self.userid}))

	def on_close(self):
		dispatcher.unregister_websocket(self.userid)

		# tell admin a user left
		admin.write_message(json.dumps({"command":"unregister", "userid":self.userid}))


	def on_message(self, message):
		dispatcher.route(message)




class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.userid = self.get_cookie('userid')
		if not self.userid:
			self.userid = get_random_id(10)
			self.set_cookie('userid', self.userid)

		rendered_template = loader.load("home.html").generate(userid=self.userid)
		self.write(rendered_template)



class DataRoute(tornado.web.RequestHandler):
	def get(self):
		self.userid = self.get_cookie('userid')
		dataset = {x:x**2 for x in range(100)}
		self.write(dataset)



class AdminSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		globals()['admin'] = self		

	def on_close(self):
		admin = None

	def on_message(self, message):
		try:
			dispatcher.route(message)

		except:
			print "there was an error handling adminsocket"



class AdminRoute(tornado.web.RequestHandler):
	def get(self):
		rendered_template = loader.load("admin.html").generate()
		self.write(rendered_template)





application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/admin', AdminRoute),
    (r'/data', DataRoute),
    (r'/signalsocket', SignalSocketHandler),
    (r'/adminsocket', AdminSocketHandler)

])
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(address="0.0.0.0", port=8000)

    print "Tornado server starting."
    tornado.ioloop.IOLoop.instance().start()


 