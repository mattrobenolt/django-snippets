from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured

try:
    from twilio import twiml
except ImportError:
    raise ImproperlyConfigured("TwimlResponse requires 'twilio-python'")

class TwimlResponse(HttpResponse):
    """ Wrapper around a Twilio Response object

    Provides a shortcut to a response with "say" or any of the other
    verbs by just passing a string argument to content,
    otherwise, accepts a full twilio.Response object.
    """

    def __init__(self, content, verb="say"):
        if isinstance(content, basestring):
            r = twiml.Response()
            try:
                getattr(r, verb.lower())(content)
            except AttributeError:
                raise AttributeError("Invalid method, `%s`" % verb)
            content = r

        super(TwimlResponse, self).__init__(
            content=content.toxml(),
            content_type='text/xml',
            status=200
        )