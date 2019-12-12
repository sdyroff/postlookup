Postlookup
==========

Update postfix transports based on mx lookups


TODO
----

* unit tests
* documentation
* logging
* try/catch exceptions ->
    * NXDOMAIN -> postmap -q "ohai" socketmap:inet:localhost:8888:fnord
    * postmap -q "ohai@localhost" socketmap:inet:localhost:8888:fnord
    * dns.resolver.NoAnswer: The DNS response does not contain an answer to the question: s.goodpoint.de. IN MX
* systemd unit
