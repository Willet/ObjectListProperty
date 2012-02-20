class ObjectListProperty(db.ListProperty):
    """A property that stores a list of serializable class instances
    Serialization / deserialization are done transparently when putting
    and getting
    
    This is a paramaterized property; the parameter must be a class with
    'serialize' and 'deserialize' methods, and all items must conform to
    this type
    
    Will store serialized objects of strings up to 500 characters in 
    length. For longer strings, change line with #! comment: 'str' ->
     'db.Text' and deal  with encoding / decoding
    
    Example:
    
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
    """
    def __init__(self, cls, *args, **kwargs):
        """Construct ObjectListProperty
        
        Args:
            cls: Class of objects in list
            *args: Optional additional arguments, passed to base class
            **kwds: Optional additional keyword arguments, passed to base class
        """
        # Ensure cls has serial / deserial methods
        if not hasattr(cls, 'serialize') or not hasattr(cls, 'deserialize'):
            raise ValueError('%s ObjectListProperty requires properties with \'serialize\' and \'deserialize\' methods' % debug_info() )
        self._cls = cls
        super(ObjectListProperty, self).__init__(str, *args, **kwargs) #!
    
    def validate_list_contents(self, value):
        """Validates that all items in the list are of the correct type.
        
        Returns:
            The validated list.
        
        Raises:
            BadValueError if the list has items are not instances of the
            cls given to the constructor.
        """
        for item in value:
            if not isinstance(item, self._cls):
                raise BadValueError('%s Items in %s must all be of type %r' % (debug_info(), self.name, self._cls))
        return value
    
    def get_value_for_datastore(self, model_instance):
        """Serialize list to send to datastore.
        
        Returns:
            validated list appropriate to save in the datastore.
        """
        obj_list = self.__get__(model_instance, model_instance.__class__)
        if obj_list is not None and type(obj_list) is list:
            db_list = []
            for obj in obj_list:
                if isinstance(obj, self._cls):
                    obj_str = obj.serialize()
                    if len(obj_str) > 500:
                        raise OverflowError('%s ObjectListProperty does not support strings over 500 characters in length' % debug_info())
                    db_list.append(obj_str)
            return db_list
        else:
            return []
    
    def make_value_from_datastore(self, db_list):
        """Deserialize datastore representation to list
        
        Returns:
            The value converted for use as a model instance attribute.
        """
        if db_list is not None and type(db_list) is list:
            return [ self._cls.deserialize(value) for value in db_list ]
        else:
            return []