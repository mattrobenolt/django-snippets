#!/usr/bin/env python

import hmac
import base64
import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.conf import settings

class HashException(Exception): pass
class InvalidSignatureException(HashException): pass

def sign_value(value, secret=None):
    return u'%s:%s' % (get_signature(value, secret))

def get_signature(value, secret=None):
    if not secret:
        secret = settings.SECRET_KEY # Pull Django's SECRET_KEY as default
    if not isinstance(value, basestring):
        value = '$p$'+base64.b64encode(pickle.dumps(value))
    key = hashlib.sha1(secret).hexdigest()
    signature = hmac.new(key, msg=value, digestmod=hashlib.sha1).hexdigest()
    return signature, value

def unsign_value(hash_, secret=None):
    try:
        value = hash_.split(':', 1)[1]
        if value.startswith('$p$'):
            value = pickle.loads(base64.b64decode(value[3:]))
        if sign_value(value, secret) == hash_:
            return value
        else:
            raise InvalidSignatureException
    except IndexError:
        raise HashException

def sign_query(querydict, signature_key='signature', secret=None):
    keys = querydict.keys()
    keys.sort()
    value = '&'.join(['%s=%s' % (k, querydict[k]) for k in keys if k != signature_key])
    return get_signature(value, secret)[0]

def verify_query(querydict, signature_key='signature', secret=None):
    if not signature_key in querydict:
        return False
    
    signature = querydict[signature_key]
    del querydict[signature_key]

    return signature == sign_query(querydict, signature_key=signature_key, secret=secret)

if __name__ == '__main__':
    secret = 'abcdefghijklmnopqrstuvwxyz'

    # Testing basic string
    assert('8a8d431c4bee603699e3fd3e9593a3264af0f57c:value1' == sign_value('value1', secret=secret))
    print "sign_value (string)...ok"
    assert(unsign_value('8a8d431c4bee603699e3fd3e9593a3264af0f57c:value1', secret=secret) == 'value1')
    print "unsign_value (string)...ok"

    # Testing basic pickling
    assert('158817702dd89fe669294d2811895215dd7432a3:$p$STEyMzQ1Ci4=' == sign_value(12345, secret=secret))
    print "sign_value (integer)...ok"
    assert(unsign_value('158817702dd89fe669294d2811895215dd7432a3:$p$STEyMzQ1Ci4=', secret=secret) == 12345)
    print "unsign_value (integer)...ok"

    # Testing a json string
    try:
        import simplejson as json
    except ImportError:
        import json
    o = {"a": True, "b": "Some value"}
    assert('c0b2108d2b90b4af6189c518a8ddcd7ea8e8e71c:{"a": true, "b": "Some value"}' == sign_value(json.dumps(o), secret=secret))
    print "sign_value (json)...ok"
    assert(unsign_value('c0b2108d2b90b4af6189c518a8ddcd7ea8e8e71c:{"a": true, "b": "Some value"}', secret=secret) == json.dumps(o))
    print "unsign_value (json)...ok"

    # Testing picking of an object
    assert('68b90a0b52b1eb1b71b07b50589ddf48f198d6b0:$p$KGRwMApTJ2EnCnAxCkkwMQpzUydiJwpwMgpTJ1NvbWUgdmFsdWUnCnAzCnMu' == sign_value(o, secret=secret))
    print "sign_value (object)...ok"
    assert(unsign_value('68b90a0b52b1eb1b71b07b50589ddf48f198d6b0:$p$KGRwMApTJ2EnCnAxCkkwMQpzUydiJwpwMgpTJ1NvbWUgdmFsdWUnCnAzCnMu', secret=secret) == o)
    print "unsign_value (object)...ok"

    assert('6b4b997b00f8c048fcbc51d44e7fe2b141153f4c' == sign_query(o, secret=secret))
    print "sign_query...ok"
    o.update({'signature': '6b4b997b00f8c048fcbc51d44e7fe2b141153f4c'})
    assert(verify_query(o, secret=secret))
    print "verify_query...ok"

    print
    print "All tests pass."
