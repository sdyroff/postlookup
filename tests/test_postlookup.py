from pynetstring import decode, encode
from postlookup import postlookup
import os
import threading
import random
import socket


def start_server(rules):
    rand = random.randint(1000, 9999)
    path = f"/tmp/postlookup-{str(rand)}.sock"
    server = postlookup.ThreadedUnixStreamServer(
        path, postlookup.PostlookupRequestHandler, rules
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


def test_postlookup_positive_match():
    rules = [
        postlookup.ForwardRule(
            "google forward", {"relay": "[testhost]:25", "pattern": "^.*google.com\.$"}
        )
    ]
    sock, server = start_server(rules)
    res = decode(client(sock, encode("mx test@gmail.com")))
    server.shutdown()
    assert len(res) == 1
    s = res[0].decode("utf-8")
    assert s.startswith("OK")
    assert "[testhost]:25" in s


def test_postlookup_no_match():
    rules = [
        postlookup.ForwardRule(
            "google forward", {"relay": "[testhost]:25", "pattern": "^.*google.com\.$"}
        )
    ]
    sock, server = start_server(rules)
    res = decode(client(sock, encode("mx test@example.com")))
    server.shutdown()
    assert len(res) == 1
    s = res[0].decode("utf-8")
    assert s.startswith("NOTFOUND")


def test_postlookup_no_mx():
    rules = [
        postlookup.ForwardRule(
            "google forward", {"relay": "[testhost]:25", "pattern": "^.*google.com\.$"}
        )
    ]
    sock, server = start_server(rules)
    res = decode(client(sock, encode("mx test@test.test.example.com")))
    server.shutdown()
    assert len(res) == 1
    s = res[0].decode("utf-8")
    assert s.startswith("NOTFOUND")
