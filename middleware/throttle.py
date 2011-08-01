import os
import time
from django.http import HttpResponse
from django.template import Context, RequestContext, loader

try:
    # Future proofing for Python 2.6
    from multiprocessing import cpu_count
except ImportError:
    def cpu_count():
         """
         Detects the number of CPUs on a system. Cribbed from pp.
         """
         # Linux, Unix and MacOS:
         if hasattr(os, "sysconf"):
             if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
                 # Linux & Unix:
                 ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
                 if isinstance(ncpus, int) and ncpus > 0:
                     return ncpus
             else: # OSX:
                 return int(os.popen2("sysctl -n hw.ncpu")[1].read())
         # Windows:
         if os.environ.has_key("NUMBER_OF_PROCESSORS"):
                 ncpus = int(os.environ["NUMBER_OF_PROCESSORS"]);
                 if ncpus > 0:
                     return ncpus
         return 1 # Default

class KeepShitChill(object):
    """
    Basic request throttling so the server won't spiral out of control.

    You must create a `503.html` page to display your own `failwhale`. :)
    """
    def process_request(self, request):
        # Calculate total load based on number of CPUs.
        # e.g., a loadavg of 4 on a computer with 8 cores, the load is 0.5.
        load = os.getloadavg()[0] / float(cpu_count())
        
        if load > 0.8: # if loads are over 80%, start throttling
            to_throttle = 0.25
            
            if load >= 0.9 and load < 1:
                to_throttle = 0.5
            elif load >= 1 and load < 10:
                to_throttle = 1
            elif load >= 10:
                # Shit's on fire!
                return server_on_fire(request)
            time.sleep(to_throttle)

def server_on_fire(request, template_name='503.html'):
    """
    503 error handler.

    Templates: `503.html`
    Context: None
    """
    t = loader.get_template(template_name) # You need to create a 503.html template.
    return HttpResponse(t.render(Context({})), status=503)