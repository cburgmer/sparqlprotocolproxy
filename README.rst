SPARQLProtocolProxy is a small proxy server based on Python's
BaseHTTPRequestHandler and exposes a SPARQL protocol interface not so strictly
following the W3C recommendation (http://www.w3.org/TR/rdf-sparql-protocol/).

What it does
============
SPARQLProtocolProxy supports any SPARQL-based triple store that rdflib and SuRF
support and makes it accessible through the standardized SPARQL protocol
interface:

* rdflib IOMemory
* MySQL (rdflib 2.4.2)
* AllegroGraph
* Sesame2
* any SPARQL protocol compliant store, and many more.

This server supports CORS, see http://enable-cors.org/.

You might want to use Deniz (http://github.com/cburgmer/deniz) to query data
exposed by this proxy.

Usage
=====
Run with::

   $ python sparqlprotocolproxy.py --cors --port 8000

Dependencies
============
* rdflib
* SuRF

And one out of:

* surf.sesame2
* surf.rdflib
* surf.allegro_franz
* surf.sparql_protocol

For example install with::

    $ easy_install SuRF surf.rdflib

Howto run with Virtuoso
=======================
Install ``surf.sparql_protocol`` and change the store settings of the
SPARQLHTTPProxy to::

   DEFAULT_STORE_SETTINGS = {'reader': "sparql_protocol",
                             'endpoint': 'http://localhost:8890/sparql'}

Contact
=======
Please report bugs to http://github.com/cburgmer/sparqlprotocolproxy/issues.

Christoph Burgmer <cburgmer (at) ira uka de>
