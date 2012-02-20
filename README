# ObjectListProperty

A Google App Engine db.ListProperty subclassed to store a list of serializable class instances. Serialization / deserialization are done transparently when putting and getting

This is a paramaterized property; the parameter must be a class with 'serialize' and 'deserialize' methods, and all items must conform to this type

Will store serialized objects of strings up to 500 characters in length. For longer strings, change line with #! comment: 'str' -> 'db.Text' and deal  with encoding / decoding

## Example

    from object_list_property import ObjectListProperty
    
    class Record:
      def __init__(self, who, timestamp=None):
        self.who = who.key() if hasattr(who, 'key') else who # Some user model
        self.timestamp = timestamp if timestamp else time.time()
    
      def serialize(self):
        return "%s@%s" % (str(self.who), str(self.time))
    
      @classmethod
      def deserialize(cls, value):
        [ who, timestamp ] = value.split('@', 1)
        return cls(who= db.Key(who), timestamp= float(timestamp))
    
    class Usage_Tracker(db.Model):
      records = ObjectListProperty(Record, indexed=False)
    
    # Assuming some User model instance 'user' exists
    usage_tracker = db.Query(Usage_Tracker).get()
    usage_tracker.records.append(Record(user))
    usage_tracker.put()