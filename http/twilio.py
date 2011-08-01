from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured

try:
    from twilio import twiml
except ImportError:
    raise ImproperlyConfigured("TwimlResponse requires 'twilio-python'")

class TwimlResponse(HttpResponse):
    """ Wrapper around a Twilio Response object

    Provides a shortcut to a response with "say" by just passing
    a string argument to content, otherwise, accepts a
    twilio.Response object.
    """

    def __init__(self, content, status=200):
        if isinstance(content, basestring):
            r = twiml.Response()
            r.say(content)
            content = r

        super(TwimlResponse, self).__init__(
            content=content.toxml(),
            content_type='text/xml',
            status=status
        )