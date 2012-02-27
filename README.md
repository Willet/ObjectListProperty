# Raison d'être

Often your Google App Engine (GAE) model needs a list of simple objects.  The general solution to storing these is to use parallel db.ListProperty's and manage both lists simultaneously. ObjectListProperty is a more elegant solution: it uses one ListProperty that stores a serialized version of your object.

# ObjectListProperty

A GAE db.ListProperty subclassed to store a list of serializable class instances. Serialization / deserialization are done transparently when putting and getting

This is a paramaterized property; the parameter must be a class with 'serialize' and 'deserialize' methods, and all items must conform to this type.

## Gotchas

Maximum serialized string length of 500 characters. For longer strings, change line with #! comment: 'str' -> 'db.Text' and deal with encoding / decoding

## Example

    from object_list_property import ObjectListProperty
    
    class Record:
      """ Our example object class, with methods serialize and deserialize.
      This stores a reference to an assumed user model and a timestamp of
      when the record was first created.

      Inputs:
        who: an assumed user model that has a db.Key
      """
      separator_char = '@'

      def __init__(self, who, timestamp=None):
        self.who = who.key() if hasattr(who, 'key') else who
        # If timestamp doesn't exist, set it to now
        self.timestamp = timestamp if timestamp else time.time()
    
      def serialize(self):
        return "%s%s%s" % (str(self.who), separator_char, str(self.time))
    
      @classmethod
      def deserialize(cls, value):
        [ who, timestamp ] = value.split(separator_char, 1)
        return cls(who= db.Key(who), timestamp= float(timestamp))
    
    class Usage_Tracker(db.Model):
      records = ObjectListProperty(Record, indexed=False)
    
    # Assuming some User model instance 'user' exists
    usage_tracker = db.Query(Usage_Tracker).get()
    usage_tracker.records.append(Record(user))
    usage_tracker.put()