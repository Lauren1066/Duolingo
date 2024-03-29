import http.server, threading, time, subprocess

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = '/index.html' if self.path == '/' else self.path
        return super().do_GET()

def run_script():
    while True:
        subprocess.run(["python", "main.py"], check=True)
        time.sleep(600)

httpd = http.server.HTTPServer(('', 27103), RequestHandler)
threading.Thread(target=run_script, daemon=True).start()
print("Serving on port 27103")
httpd.serve_forever()
