"""
JSON utilities for the P3IF framework.

This module provides utilities for JSON encoding and decoding of P3IF objects.
"""
import json
from datetime import datetime

class P3IFEncoder(json.JSONEncoder):
    """
    JSON encoder that can handle datetime objects and P3IF objects.
    
    This encoder will:
    1. Convert datetime objects to ISO format strings
    2. Convert P3IF objects to dictionaries using their dict() method if available
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):
            # Convert all P3IF objects to dict
            obj_dict = obj.dict()
            # Also handle datetime objects in the dict
            for key, value in obj_dict.items():
                if isinstance(value, datetime):
                    obj_dict[key] = value.isoformat()
            return obj_dict
        return super().default(obj)

def convert_to_serializable(obj):
    """
    Convert an object to a JSON serializable format.
    
    Args:
        obj: The object to convert
        
    Returns:
        A JSON-serializable version of the object
    """
    if hasattr(obj, 'dict'):
        result = obj.dict()
        # Convert datetime objects to ISO format
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result
    return obj

def dumps(obj, **kwargs):
    """
    Serialize obj to a JSON formatted string using the P3IFEncoder.
    
    This is a wrapper around json.dumps that uses the P3IFEncoder.
    
    Args:
        obj: The object to serialize
        **kwargs: Additional keyword arguments to pass to json.dumps
        
    Returns:
        A JSON formatted string
    """
    return json.dumps(obj, cls=P3IFEncoder, **kwargs)

def dump(obj, fp, **kwargs):
    """
    Serialize obj as a JSON formatted stream to fp using the P3IFEncoder.
    
    This is a wrapper around json.dump that uses the P3IFEncoder.
    
    Args:
        obj: The object to serialize
        fp: A file-like object with a write() method
        **kwargs: Additional keyword arguments to pass to json.dump
    """
    return json.dump(obj, fp, cls=P3IFEncoder, **kwargs)

def loads(s, **kwargs):
    """
    Deserialize s (a str, bytes or bytearray instance) to a Python object.
    
    This is a wrapper around json.loads.
    
    Args:
        s: A JSON string
        **kwargs: Additional keyword arguments to pass to json.loads
        
    Returns:
        A Python object
    """
    return json.loads(s, **kwargs)

def load(fp, **kwargs):
    """
    Deserialize fp (a file-like object) to a Python object.
    
    This is a wrapper around json.load.
    
    Args:
        fp: A file-like object with a read() method
        **kwargs: Additional keyword arguments to pass to json.load
        
    Returns:
        A Python object
    """
    return json.load(fp, **kwargs) 