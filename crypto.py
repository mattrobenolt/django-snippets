import hmac

from django.conf import settings
from django.utils.hashcompat import sha_constructor, sha_hmac


class HashException(Exception): pass
class InvalidSignatureException(HashException): pass

def sign_value(value):
    return u'%s:%s' % (get_signature(value), value)

def get_signature(value):
    key = sha_constructor(settings.SECRET_KEY).digest()
    signature = hmac.new(key, msg=value, digestmod=sha_hmac).hexdigest()
    return signature

def unsign_value(hash_):
    try:
        value = hash_.split(':')[1]
        if sign_value(value) == hash_:
            return value
        else:
            raise InvalidSignatureException
    except IndexError:
        raise HashException

def sign_query(querydict, signature_key='signature'):
    keys = obj.keys()
    keys.sort()
    value = '&'.join(['%s=%s' (k, obj[k]) for k in keys if k != signature_key])
    return get_signature(value)

def verify_query(obj, signature_key='signature'):
    if not signature_key in obj:
        return False
    
    signature = obj[signature_key]
    del obj[signature_key]

    return signature == get_signature(obj)