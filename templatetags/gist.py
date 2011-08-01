from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor

import urllib2

register = Library()

class GistNode(Node):
    def __init__(self, gist_id, filename=None, *args):
        self.gist_id = gist_id
        self.filename = filename
        self.args = args
    
    def _render(self, gist_id, filename):
        url = "https://gist.github.com/%s.js" % gist_id
        if filename is not None:
            url += '?file=%s' % filename
        return u'<script src="%s"></script>' % url

    def render(self, context):
        # Try to resolve gist_id as a context variable. If not, assume the actual value.
        try:
            gist_id = Variable(self.gist_id)
            gist_id = gist_id.resolve(context)
        except VariableDoesNotExist:
            gist_id = self.gist_id
        
        if self.filename is not None:
            # Try to resolve filename as a context variable. If not, assume the actual value.
            try:
                filename = Variable(self.filename)
                filename = filename.resolve(context)
            except VariableDoesNotExist:
                filename = self.filename
        else:
            filename = None
        
        return self._render(gist_id, filename)

class GistRawNode(GistNode):
    def _render(self, gist_id, filename):
        # Try to see if filename was left off and a cache_time was specified instead.
        # This must be done first to determine what the final request url is.
        try:
            cache_time = int(filename)
            filename = None
        except ValueError:
            cache_time = None
        
        url = 'https://raw.github.com/gist/%s' % gist_id
        if filename is not None:
            url += '/%s' % filename
        # Build a cache key based on the url being requested
        cache_key = '__gistraw:%s' % md5_constructor(url).hexdigest()
        response = cache.get(cache_key)
        if not response:
            try:
                response = urllib2.urlopen(url).read()
            except urllib2.HTTPError:
                return '' # Return empty string if any error occurs and avoid caching
            
            if cache_time is None:
                try:
                    cache_time = int(self.args[0]) # Check if an optional cache_time was passed in args
                except (IndexError, ValueError):
                    cache_time = 86400 # 60 * 60 * 24 (24 hours)
            cache.set(cache_key, response, cache_time)
        return response

def do_gist(parser, token, raw=False):
    tokens = token.split_contents()
    if len(tokens) == 1:
        raise TemplateSyntaxError(u"'%r' tag requires at least 1 argument." % tokens[0])
    
    if raw:
        return GistRawNode(*tokens[1:])
    else:
        return GistNode(*tokens[1:])

@register.tag
def gist(parser, token):
    """
    Render a GitHub gist embed code.

    Usage::
    
        {% load gist %}
        {% gist [gist_id] %}

    This tag also supports an optional filename variable::

        {% load gist %}
        {% gist [gist_id] [filename] %}
    
    Examples::
    
        {% gist "0e3e758a56a45587c7d5" %}
        {% gist "0e3e758a56a45587c7d5" "file2.html" %}
    """
    return do_gist(parser, token, raw=False)
    

@register.tag
def gistraw(parser, token):
    """
    Embed the raw GitHub gist, and cache it for future lookups.
    Default cache duration is 24 hours.

    Usage::

        {% load gist %}
        {% gistraw [gist_id] %}

    This tag also supports an optional filename variable and/or cache time::

        {% load gist %}
        {% gistraw [gist_id] [filename] [cache_time] %}
        {% gistraw [gist_id] [cache_time] %}
    
    Examples::
    
        {% gistraw "0e3e758a56a45587c7d5" %}
        {% gistraw "0e3e758a56a45587c7d5" "file1.html %}
        {% gistraw "0e3e758a56a45587c7d5" "file1.html" 3600 %}
        {% gistraw "0e3e758a56a45587c7d5" 3600 %}
    """
    return do_gist(parser, token, raw=True)