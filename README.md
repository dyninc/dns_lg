Dyn dns_lg
======

This application implements an DNS Looking Glass. The application is intended to be deployed in multiple locations around the world. Using a REST based API, it is possible to remotely query DNS settings via each Looking Glass. This allows for checking geographic dependent behavior.

This implementation is loosely based on the DNS Looking Glass described by Stephan Bortzmeyer: http://www.bortzmeyer.org/dns-lg.html

License
======

See LICENSE for details

Requirements
======
Requires at a minimum: Python, ldns, Python-ldns, Python-flask

ldns must be downloaded and built with support for python:

```
%: wget -nc https://www.nlnetlabs.nl/downloads/ldns/ldns-1.6.16.tar.gz
%: tar -xzf ldns-1.6.16.tar.gz
%: ./configure --with-pyldns
%: make
%: make install
```

Installation
======
A Puppet script is included to simplify installation. It will download all requirements and launch the application behind NGINX using supervisord.

The puppet script has only been tested on Ubuntu 12.04 64-bit instances, but should work else where.

With a minimum install it is possible to run the application by running:

```
%: python api.py
```

Then you can test by using curl:

```
%: curl http://0.0.0.0:8185/dyn.com/
```

Usage
======
This program implements a REST based API to using the ldns library for DNS queries. This allows the user to use ordinary HTTP requests to access DNS data. The DNS data is returned in a JSON format as proposed by <http://tools.ietf.org/html/draft-bortzmeyer-dns-json>. However, this implementation may differ from the proposal.

If the Looking Glass is installed at http://lg.example.com/, the URL for queries will be http://lg.example.com/$DOMAIN[/$TYPE][/$CLASS] where DOMAIN is the domain name, TYPE is a DNS record type, and CLASS is generally "IN".

Several options exist for modifying the query:
  * server=  can be used to specify which server to address the query to. Can be a FQDN or IP address.
  * flags=   can be used to force a non-recursive server answer by setting the value to "rd".
  * format=  can be used to specify the return data format. JSON is the only format supported at this time.

Some example queries:

    http://lg.example.com/dyn.com/A/IN/
    http://lg.example.com/dyn.com/A/IN/?server=a.root-servers.net
    http://lg.example.com/dyn.com/A/IN/?server=216.146.35.35
    http://lg.example.com/dyn.com/A/IN/?server=a.root-servers.net&flags=rd
  
TODO
======

 - Multiple return formats
 - DNSSEC RR Type queries.

