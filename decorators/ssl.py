from django.conf import settings
from django.http import HttpResponseRedirect

def secure_required(view_func):
    """Decorator makes sure URL is accessed over https.
    
    Note: Use with EnforceSSL middleware.
    """
    def _wrapped_view_func(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    _wrapped_view_func.ssl = True
    return _wrapped_view_func

def insecure_required(view_func):
    """Decorator makes sure URL is accessed over http.
    
    Note: Use with EnforceSSL middleware.
    """
    def _wrapped_view_func(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    _wrapped_view_func.ssl = False
    return _wrapped_view_func