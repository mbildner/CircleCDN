import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options




class HomePageHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("""
			<!DOCTYPE html>
			<html>
				<body>
					<h1>Homepage</h1>
					<p id="newmessage"></p>
					<input id="sendmessage"></input>
					<script>
						var websocket = new WebSocket('ws://localhost:8000/websocket');
						websocket.onmessage = function (m) {
							var newmessage = document.getElementById('newmessage');
							newmessage.innerText = m.data;
						}
						document.getElementById('sendmessage')
							.addEventListener('keypress', function (k) {
								if (k.which===13) {
									websocket.send(this.value);
								}
							});
					</script>
				</body>
			</html>
			""")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print "new connection"

	def on_close(self):
		pass

	def on_message(self, message):
		self.write_message(message)




application = tornado.web.Application([
    (r'/websocket', WebSocketHandler),
    (r'/', HomePageHandler)


])
 




if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(address="0.0.0.0", port=8000)
    tornado.ioloop.IOLoop.instance().start()