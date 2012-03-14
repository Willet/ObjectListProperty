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
from django.utils import simplejson
from google.appengine.ext import db


class ObjectListProperty(db.ListProperty):
    """A property that stores a list of serializable class instances.
    Serialization / deserialization are done transparently when putting
    and getting.  This is a paramaterized property; the parameter must be a
    class with serializable members.

    ObjectListProperty optionally uses 'serialize' and 'deserialize' methods
    from the item class if they exist, otherwise a JSON representation of the
    item's internal dict is used.  These methods should be implemented if the
    class has attributes that are not builtin types.
    
    Note: can store serialized objects of strings up to 500 characters in 
    length. For longer strings, change line with #! comment: 'str' ->
     'db.Text' and handle with encoding / decoding
    
    Example:
    
    class Record():
        def __init__(self, who, timestamp=None):
            self.who = who.key() if hasattr(who, 'key') else who # Some user model
            self.timestamp = timestamp if timestamp else time.time()
    
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
        self._cls = cls

        super(ObjectListProperty, self).__init__(str, *args, **kwargs) #!

    def __repr__(self):
        return '<%s.%s at %s\n%s> containing <%s.%s>' % (self.__class__.__module__,
                                        self.__class__.__name__,
                                        hex(id(self)), 
                                        str('\n '.join('%s : %s' % (k, repr(v)) 
                                            for (k, v) in self.__dict.iteritems())),
                                        self._cls.__class__.__module__,
                                        self._cls.__class__.__name__)
    
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
                raise db.BadValueError('%s Items in %s must all be of type %r' % (debug_info(), self.name, self._cls) )
        return value
    
    def get_value_for_datastore(self, model_instance):
        """Serialize list to send to datastore.
        
        Returns:
            validated list appropriate to save in the datastore.
        """
        if hasattr(self._cls, 'serialize') and callable(getattr(self._cls, 'serialize')):
            def item_to_string(i):
                return i.serialize()
        else:
            def item_to_string(i):
                return simplejson.dumps(i.__dict__)

        obj_list = self.__get__(model_instance, model_instance.__class__)
        if obj_list is not None and type(obj_list) is list:
            db_list = []

            for obj in obj_list:

                if isinstance(obj, self._cls):
                    obj_str = item_to_string(obj)

                    if not len(obj_str) > 500:
                        db_list.append(obj_str)
                    else:
                        raise OverflowError('%s %s does not support object serialization \
                                             over 500 characters in length.  Substitute str representation \
                                             for db.Text in %s.%s' % (debug_info(),
                                                                      self.name,
                                                                      self.__class__.__module__,
                                                                      self.__class__.__name__))    
            return db_list
        else:
            return []
    
    def make_value_from_datastore(self, db_list):
        """Deserialize datastore representation to list
        
        Returns:
            The value converted for use as a model instance attribute.
        """
        if hasattr(self._cls, 'deserialize') and callable(getattr(self._cls, 'deserialize')):
            def string_to_item(s):
                return self._cls.deserialize(s)
        else:
            def string_to_item(s):
                return self._cls(**(simplejson.loads(s)))

        if db_list is not None and type(db_list) is list:
            return [ string_to_item(value) for value in db_list ]
        else:
            return []