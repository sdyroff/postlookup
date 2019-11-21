from pynetstring import decode, encode
from postlookup import postlookup
import threading
import random
import socket


def start_server():
    rand = random.randint(1000, 9999)
    path = f"/tmp/postlookup-{str(rand)}.sock"
    server = postlookup.ThreadedUnixStreamServer(
        path, postlookup.PostlookupRequestHandler
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return path, server


def client(s, message):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(s)
        sock.sendall(message)
        response = sock.recv(1024)
        return response


def test_postlookup():
    sock, server = start_server()
    res = decode(client(sock, encode("name test@gmail.com")))
    server.shutdown()
    assert len(res) == 1
    s = res[0].decode("utf-8")
    assert s.startswith("OK")
    assert "google.com" in s
