from django.http import HttpResponse

try:
    # Preferred because of the simplejson C library
    import simplejson as json
except ImportError:
    try:
        # Fall back to Python 2.6 built-in version
        import json
    except ImportError:
        # As a last ditch effort, try and get the version from Django
        from django.utils import simplejson as json

class JsonResponse(HttpResponse):
    def __init__(self, content, status=200):
        super(JsonResponse, self).__init__(
            content=json.dumps(content),
            content_type='application/json',
            status=status
        )