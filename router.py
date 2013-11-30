from RTCManager import Master, Dispatcher, DataManager, PeerConnectionManager, get_random_id

import json
import os
from random import choice

# remove database imports and logic to wrapped up functions elsewhere
import sqlite3
conn = sqlite3.connect(os.path.join('static', 'campaign_finance_data.db'))



import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options
from tornado import template




dispatcher = Dispatcher()
datamanager = DataManager()
peerconnectionmanager = PeerConnectionManager()

master = Master(dispatcher, peerconnectionmanager, datamanager)

def get_zipcode_contributions(zipcode):
	c = conn.cursor()
	query = c.execute('''SELECT i.Contrib, SUM(i.Amount), c.FirstLastP, c.Party FROM Individuals i JOIN Candidates c ON (i.RecipID=c.CID) WHERE i.Zip=? GROUP BY i.Contrib''', (zipcode,))
	return c.fetchall()
	

# -------------------------------------------------
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.userid = self.get_cookie('userid')
		if not self.userid:
			self.userid = get_random_id(10)
			self.set_cookie('userid', self.userid)


		# for now limit users to 10 zipcodes

		zipcodes = ['06830', '90210', '60045', '06880','10022',
						'60093', '07901', '30327', '78746','90272']

		self.render("home.html", userid=self.userid, datasets=zipcodes)


class SignalSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.userid = self.get_cookie('userid')
		master.register_websocket(self.userid, self)
		# master.register_peer(self.userid)

	def on_close(self):
		master.unregister_websocket(self.userid)
		# master.unregister_peer(self.userid)

	def on_message(self, message):
		master.handle_message(message)



class DataRequestRoute(tornado.web.RequestHandler):
	def get(self):
		userid = self.get_cookie('userid')
		dataset_id = self.get_argument('zipcode')

		serving_peers = master.datamanager.get_serving_peers(dataset_id)

		if not serving_peers:
			dataset = get_zipcode_contributions(dataset_id)

			self.write(json.dumps(dataset))

			master.datamanager.register_dataset(dataset_id)
			master.datamanager.register_serving_peer(dataset_id, userid)

		else:
			serving_peer = choice(serving_peers)
			master.connect_users(userid, serving_peer)
			# where does this code go? -- we are telling the user that its request is being rerouted to a peer, is that opaque? transparent?
			self.write("peer_reroute")


class AdminRoute(tornado.web.RequestHandler):
	def get(self):
		self.render("admin.html")



class AdminSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		pass

	def on_close(self):
		pass

	def on_message(self, message):
		pass



class LoginRoute(tornado.web.RequestHandler):
	def get(self):
		self.render('login.html')

	def post(self):
		pass






application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/admin', AdminRoute),
    (r'/signalsocket', SignalSocketHandler),
    (r'/adminsocket', AdminSocketHandler),
    (r'/dataroute', DataRequestRoute)

], template_path=os.path.join(os.getcwd(), "templates"), static_path=os.path.join(os.getcwd(), "static"))
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(address="0.0.0.0", port=8000)

    print "Tornado server starting.  Shit's about to get real."
    tornado.ioloop.IOLoop.instance().start()


 