from RTCManager import Master, Dispatcher, DataManager, PeerConnectionManager, get_random_id

import json
import sqlite3
import os

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

master = Master(dispatcher, datamanager, peerconnectionmanager)

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
		desired_zipcode = self.get_argument('zipcode')
		dataset = get_zipcode_contributions(desired_zipcode)
		self.write(json.dumps(dataset))

		

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


 