#!/usr/bin/env python
#
# Copyright (c) 2012 Fraser Harris
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, without conditions.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
import time

from django.utils import simplejson

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util

from object_list_property import ObjectListProperty


### Models for this example ###

class SimpleObject():
    """ The simple object that will be in first ObjectListProperty.

    Its safe to rely on the built-in ObjectListProperty serialization because
    the attributes have JSON representation.

    For this example, it stores some information about each page request
    """
    def __init__(self, user_agent, email=None, referer=None, timestamp=None):
        """ The built-in ObjectListProperty serialization will send in parameters
        that exactly match the attribute names.
        """
        self.user_agent = user_agent
        self.referer = referer
        self.email = email
        self.timestamp = timestamp if timestamp else time.time()


class ComplexObject():
    """ This 'complex' object will be in our 2nd ObjectListProperty

    We've defined example serialize and deserialize methods for
    ObjectListProperty to use.

    For this example, it stores random information
    """
    def __init__(self, random=None):
        from random import randint

        if not random:
            random = []
        random.append(randint(1000, 9999))
        self.random = random

    def __str__(self):
        return ''.join([ '%i ' % (i,) for i in self.random ])
    
    def serialize(self):
        return simplejson.dumps(self.random)
    
    @classmethod
    def deserialize(cls, value):
        return cls(random=simplejson.loads(value))


class Requesters(db.Model):
    """ Our model that uses ObjectListProperty, parameterized with 
    1) SimpleObject, which uses the built-in serialization, and
    2) ComplexObject, which defines its own serialization
    """
    records = ObjectListProperty(SimpleObject)
    salts = ObjectListProperty(ComplexObject)
    other_property = db.StringProperty
    etc_property = db.FloatProperty


### Web request handler ###

class ShowRequesters(webapp.RequestHandler):
    def get(self):
        # Implicit in get is deserializing the ObjectListProperty items
        reqs = Requesters.all().get()

        if not reqs:
            reqs = Requesters()
        if not reqs.salts:
            reqs.salts.append(ComplexObject())

        # Create a record for this request
        record = SimpleObject(user_agent=self.request.headers.get('User-Agent'),
                        email=self.request.headers.get('From'),
                        referer=self.request.headers.get('Referer'))

        # We can use our ObjectListProperty just like a list of SimpleObject's
        reqs.records.append(record)

        # Implicit in put is serializing the ObjectListProperty items
        reqs.put()

        # Write response
        resp_html = """
            <html>
    	    <head>
    	    </head>
    	    <body>
                <h1>Requests recieved:</h1>
                <ol>"""

        # Lets iterate over our ObjectListProperty
        for r in reqs.records:
    	    resp_html += '<li>%s %s %s %s</li>' % (r.email, r.user_agent, r.referer, r.timestamp)
    	
        resp_html += """
                </ol>
                <h1>Salts stored:</h1>
                <ol>
                    <li>%s</li>
                </ol>
            </body>""" % (reqs.salts[0],)

        self.response.out.write(resp_html)


def main():
    application = webapp.WSGIApplication([('/', ShowRequesters)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
