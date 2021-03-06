import re
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

# Reserved words list from http://javascript.about.com/library/blreserved.htm
JAVASCRIPT_RESERVED_WORDS = frozenset([
    'abstract', 'as', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
    'class', 'continue', 'const', 'debugger', 'default', 'delete', 'do', 'double',
    'else', 'enum', 'export', 'extends', 'false', 'final', 'finally', 'float',
    'for', 'function', 'goto', 'if', 'implements', 'import', 'in', 'instanceof',
    'int', 'interface', 'is', 'long', 'namespace', 'native', 'new', 'null',
    'package', 'private', 'protected', 'public', 'return', 'short', 'static',
    'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient',
    'true', 'try', 'typeof', 'use', 'var', 'void', 'volatile', 'while', 'with',
])
JAVASCRIPT_FUNCTION_PATTERN = re.compile(r'^[$a-z_][0-9a-z_\.\[\]]*$', re.I)

class JsonResponse(HttpResponse):
    def __init__(self, content, status=200, callback=None):
        content_ = json.dumps(content, separators=(',',':'), cls=DjangoJSONEncoder)
        if callback:
            try:
                callback = callback.strip()
                if JAVASCRIPT_FUNCTION_PATTERN.match(callback):
                    if not callback in JAVASCRIPT_RESERVED_WORDS:
                        content_ = '%s(%s)' % (callback, content_)
            except:
                # callback probably wasn't a string
                pass
        super(JsonResponse, self).__init__(
            content=content_,
            content_type='application/json',
            status=status
        )