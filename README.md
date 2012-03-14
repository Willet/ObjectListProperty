# ObjectListProperty - a flexible list property for App Engine

Version: 0.2, last updated Mar. 14, 2012

A Google App Engine (GAE) Python db.ListProperty subclassed to store a list of serializable class instances. Serialization / deserialization are done transparently when putting and getting. This is a paramaterized property; the parameter must be a class with serializable members.

ObjectListProperty optionally uses 'serialize' and 'deserialize' methods from the item class if they exist, otherwise a JSON representation of the item's internal dict is used.  These methods should be implemented if the class has attributes that are not builtin types.

# Raison d'être

Often your GAE model needs a list of simple objects.  The general solution to storing these is to use parallel db.ListProperty's and manage both lists simultaneously. ObjectListProperty is a more elegant solution: it uses one ListProperty that stores a serialized version of your object.

## Gotchas

Maximum serialized string length of 500 characters. For longer strings, change line with #! comment: 'str' -> 'db.Text' and deal with encoding / decoding

## Examples

    class Record():
        """ A simple object that we want to store with our model """
        def __init__(self, who, timestamp=None):
            self.who = who.key() if hasattr(who, 'key') else who # Some user model
            self.timestamp = timestamp if timestamp else time.time()
    
    class Usage_Tracker(db.Model):
        records = ObjectListProperty(Record, indexed=False)

See /example/main.py for a working App Engine example

## Testing

Tested on Google App Engine Python SDK 1.6.3

## Release History

0.2 - (3/14/2012) Added internal serialization using json and __dict__
0.1 - (2/20/2012) First public version

## License

Copyright (c) Fraser Harris, 2012
No restrictions on usage.