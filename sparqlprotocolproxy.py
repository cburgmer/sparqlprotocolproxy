#!/usr/bin/python

# Anything in this __doc__ string is served under 'http://host:port/'
"""
SPARQLProtocolProxy is a small proxy server based on Python's
BaseHTTPRequestHandler and exposes a SPARQL protocol interface not so strictly
following the W3C recommendation.

SPARQLProtocolProxy supports any SPARQL-based triple store that rdflib and SuRF
support and makes it accessible through the standardized SPARQL protocol
interface:

* rdflib IOMemory
* MySQL (rdflib 2.4.2)
* AllegroGraph
* Sesame2
* any SPARQL protocol compliant store, and many more.

This server supports CORS, see http://enable-cors.org/.

You might want to use Deniz (http://github.com/cburgmer/deniz) to query the data
exposed by this proxy.
"""

__all__ = ['SPARQLProtocolProxy']

__version__ = '0.1'

from optparse import OptionParser
import os
import shutil
from StringIO import StringIO
import time
import json
import urllib
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from surf.store import Store

# TODO try to make these options non-global
class Options(object):
    def __init__(self, cors=False, index_file=None):
        self.cors = cors
        self.index_file = index_file

options = Options()

def query_params(query_str):
    """Convert the query string to a dict of parameters."""
    params = {}
    for kv_pair in query_str.split('&'):
        key, value = kv_pair.split('=', 1)
        params[key] = urllib.unquote_plus(value)
    return params

class SPARQLProtocolProxy(BaseHTTPRequestHandler):
    """HTTP server exposing a SPARQL protocol endpoint."""
    @property
    def store(self):
        if not hasattr(self, '__store'):
            STORE_SETTINGS = {'reader': "rdflib",
                              'writer': "rdflib",
                              'rdflib_store': 'IOMemory'}
            self.__store = Store(**STORE_SETTINGS)
        return self.__store

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def _respond_index(self):
        """Respond where an index.html is expected."""
        global options

        if options.index_file:
            try:
                # Always read in binary mode. Opening files in text mode may
                # cause newline translations, making the actual size of the
                # content transmitted *less* than the content-length!
                f = open(options.index_file, 'rb')
            except IOError:
                self.send_error(404, "File not found")
                return

            fs = os.fstat(f.fileno())
            length = str(fs[6])
            date_time = fs.st_mtime
        else:
            f = StringIO()
            f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
            f.write("<html>\n<title>SparqlProtocolProxy</title>\n")
            f.write("<body>\n<h2>SparqlProtocolProxy</h2>\n")
            f.write('<p>'
                    + __import__('sparqlprotocolproxy').__doc__\
                        .replace('\n\n', '</p>\n<p>').replace('\n*', '<br/>\n*')
                    + '</p>')
            f.write("</body>\n</html>\n")
            length = f.tell()
            f.seek(0)
            date_time = time.time()

        self.send_response(200)
        self.send_header("Content-Length", length)
        self.send_header("Content-type", 'text/html; charset=UTF-8')
        self.send_header("Last-Modified", self.date_time_string(date_time))
        if options.cors:
            self.send_header("Access-Control-Allow-Origin", '*')
        self.end_headers()

        return f

    def _respond_query(self, query):
        """Answer query."""
        params = query_params(query) if query else {}

        if 'query' not in params:
            self.send_error(400, "No 'query' parameter specified")
            return

        f = StringIO()
        response = self.store.execute_sparql(params['query'])
        try:
            response_str = json.dumps(response)
        except TypeError:
            # Workaround for surf_rdflib plugin
            response_str = response.serialize('json')
        f.write(response_str)
        length = f.tell()
        f.seek(0)

        self.send_response(200)
        self.send_header("Content-Length", str(length))
        self.send_header("Content-type", 'application/sparql-results+json')
        if options.cors:
            self.send_header("Access-Control-Allow-Origin", '*')
        self.end_headers()

        return f

    def send_head(self):
        global options

        i = self.path.rfind('?')
        if i >= 0:
            path, query = self.path[:i], self.path[i+1:]
        else:
            path, query = self.path, ''

        path = path.strip('/')
        if path == 'sparql':
            return self._respond_query(query)
        elif path == '':
            return self._respond_index()
        else:
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
            return None

def run():
    global options

    import logging
    logging.basicConfig(level=logging.INFO)
    parser = OptionParser(version="%prog " + __version__)
    parser.add_option("--cors",
                    action="store_true", dest="cors", default=False,
                    help="Enable cors, see http://enable-cors.org/")
    parser.add_option("-s", "--host", dest="host", default='127.0.0.1',
                    help="run server on HOST", metavar="HOST")
    parser.add_option("-p", "--port", dest="port", type="int", default=8000,
                    help="run server on PORT", metavar="PORT")
    parser.add_option("--index", dest="index_file", default=None,
                    help="serve FILE as index.html", metavar="FILE")

    options, args = parser.parse_args()

    httpd = HTTPServer((options.host, options.port), SPARQLProtocolProxy)
    logging.info("Starting up on %s:%s" % (options.host, options.port))
    httpd.serve_forever()

if __name__ == "__main__":
    run()
