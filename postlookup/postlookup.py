#!/usr/bin/env python3

from pynetstring import Decoder, encode
from dns import resolver
from email_split import email_split
import socket
import socketserver
import configparser
import os
import re

rules = []


class PostlookupRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        decoder = Decoder()
        raw_query = []
        try:
            while not raw_query:
                data = self.request.recv(4096)
                part = decoder.feed(data)
                if part:
                    raw_query = raw_query + part
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


class ForwardRule:
    def __init__(self, name, entry):
        self.name = name
        self.relay = entry["relay"]
        self.pattern = re.compile(entry["pattern"])

    def __str__(self):
        return f"{self.name} ({self.pattern} -> {self.relay})"

    def __repr__(self):
        return f"ForwardRule({str(self)})"


def openconfig(files=["/etc/postlookup", os.path.expanduser("~/.postlookup")]):
    config = configparser.ConfigParser()
    for conffile in files:
        try:
            with open(conffile, "r", encoding="utf-8") as cf:
                config.read_file(cf)
                print(f"reading config from {conffile}")
                return config
        except Exception:
            pass
    raise Exception("Could not find a config file")


def main():
    global rules
    config = openconfig()
    path = config["general"].get("socket")

    rules = [
        ForwardRule(section, config[section])
        for section in config.sections()
        if not section == "general"
    ]

    server = ThreadedUnixStreamServer(path, PostlookupRequestHandler)
    with server:
        server.serve_forever()


if __name__ == "__main__":
    main()
