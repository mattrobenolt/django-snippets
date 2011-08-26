import os
import time
from django.conf import settings
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

if not getattr(settings, 'THROTTLE_CONFIG', None) or not isinstance(settings.THROTTLE_CONFIG, ThrottleConfig):
    config = ThrottleConfig()
    config.add(load=0.8, wait=0.25)
    config.add(load=0.9, wait=0.5)
    config.add(load=1.0, wait=1)
    config.add(load=10)
    THROTTLE_CONFIG = config
else:
    THROTTLE_CONFIG = settings.THROTTLE_CONFIG


class ThrottleError(Exception):
    pass

class ThrottleConfig(object):
    vals = {}
    def add(self, load, wait=None):
        if not isinstance(load, (int, float)):
            raise ValueError("Load must be an int or float.")
        if not load > 0:
            raise ValueError("Load must be greater than 0")
        if wait is not None and not isinstance(wait, (int, float)):
            raise ValueError("Wait must be an int, float, or None")
        elif wait is not None and not wait > 0:
            raise ValueError("Wait must be greater than 0")
        self.vals[load] = wait
    
    def dump(self):
        return self.vals
    
    def __repr__(self):
        return u"<ThrottleConfig %s>" % self.vals.__repr__()

class KeepShitChill(object):
    """Basic request throttling so the server won't spiral out of control.

    You must create a `503.html` page to display your own `failwhale`. :)
    """
    def __init__(self):
        config = THROTTLE_CONFIG.dump()
        limits = config.keys()
        limits.sort()
        self.min = limits[0]

        limits.reverse()
        self.thresholds = [(k, THROTTLE_THRESHOLDS[k]) for k in limits]
    
    def __throttle(self, load):
        to_throttle = 0
        if load > self.min:
            for limit in self.thresholds:
                if load > limit[0]:
                    to_throttle = limit[1]
                    break
            
            if to_throttle is None:
                raise ThrottleError("Server on fire!")
        
        return to_throttle

    def process_request(self, request):
        # Calculate total load based on number of CPUs.
        # e.g., a loadavg of 4 on a computer with 8 cores, the load is 0.5.
        load = os.getloadavg()[0] / float(cpu_count())

        try:
            to_throttle = self.__throttle(load)
        except ThrottleError:
            return server_on_fire(request)
        
        if to_throttle > 0:
            time.sleep(to_throttle)
    
    def test(self, load):
        return self.__throttle(load)

def server_on_fire(request, template_name='503.html'):
    """
    503 error handler.

    Templates: `503.html`
    Context: None
    """
    t = loader.get_template(template_name) # You need to create a 503.html template.
    return HttpResponse(t.render(Context({})), status=503)