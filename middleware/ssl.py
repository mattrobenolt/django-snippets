from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

class EnforceSSL(object):
    """Enforce SSL or non-SSL connection with decorator, or automatically redirect based on user.is_authenticated()

    Note: Can be used with my ssl decorator.
    Can be turned off globally by setting `HTTPS_SUPPORT = False` in settings.py.

    If only the middleware is used, the connection is automatically secured if the user
    is logged in. If not, they are forced to HTTP connection.

    Wrap your view in @secure_required or @insecure_required:

    @secure_required
    def login(request):
        ...
    
    @insecure_required
    def somepage(request):
        ...
    """
    def __init__(self):
        if not getattr(settings, 'HTTPS_SUPPORT', True):
            from django.core.exceptions import MiddlewareNotUsed
            raise MiddlewareNotUsed()
    
    def process_view(self, request, view_func, *args, **kwargs):
        ssl = getattr(view_func, 'ssl', None)
        if (request.user.is_authenticated() or ssl == True) and request.META['SERVER_PORT'] != '443':
            if settings.DEBUG and request.method == 'POST':
                raise RuntimeError("Cannot perform an SSL redirect while maintaining POST data.")
            
            request_url = request.build_absolute_uri(request.get_full_path())
            secure_url = request_url.replace('http://', 'https://')
            return HttpResponseRedirect(secure_url)
        
        elif ssl == False and not request.user.is_authenticated() and request.META['SERVER_PORT'] != '80':
            if settings.DEBUG and request.method == 'POST':
                raise RuntimeError("Cannot perform an SSL redirect while maintaining POST data.")
            
            request_url = request.build_absolute_uri(request.get_full_path())
            secure_url = request_url.replace('https://', 'http://')
            return HttpResponseRedirect(secure_url)
        
        elif ssl == None and not request.user.is_authenticated() and request.META['SERVER_PORT'] == '443':
            if settings.DEBUG and request.method == 'POST':
                raise RuntimeError("Cannot perform an SSL redirect while maintaining POST data.")
            
            request_url = request.build_absolute_uri(request.get_full_path())
            secure_url = request_url.replace('https://', 'http://')
            return HttpResponseRedirect(secure_url)