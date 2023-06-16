# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import database

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(bytes('object:{"id":"1", "name" : "Ivan"}', "utf-8"))

    def do_POST(self):
        print("post")

if __name__ == "__main__":

    ## establish database connection

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")