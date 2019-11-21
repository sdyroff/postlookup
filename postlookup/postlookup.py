#!/usr/bin/env python3

# The socketmap protocol:
#   http://www.postfix.org/socketmap_table.5.html

from pynetstring import decode, encode
from dns import resolver
from email_split import email_split
import socket
import threading
import socketserver


class PostlookupRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            # postfix accepts only 100000 in a reply we can do the same
            data = self.request.recv(10000)
            raw_query = decode(data)
            if len(raw_query) != 1:
                result = "PERM Got not exactly one query"
            else:
                query = raw_query[0][4:].decode().strip()
                print(f"Received {query!r}")

                email = email_split(query)

                mxs = sorted(
                    resolver.query(email.domain, "MX"), key=lambda x: x.preference
                )
                lowest_prio_mx = mxs[0].exchange.to_text()
                result = f"OK [{lowest_prio_mx}]"

            self.request.sendall(encode(result))
        except Exception as e:
            print("Error during lookup: " + str(e))
            self.request.sendall(encode("NOTFOUND"))
        finally:
            self.request.close()


class ThreadedUnixStreamServer(
    socketserver.ThreadingMixIn, socketserver.UnixStreamServer
):
    pass


def main():
    path = "test.sock"

    server = ThreadedUnixStreamServer(path, PostlookupRequestHandler)
    with server:
        server.serve_forever()


if __name__ == "__main__":
    main()
