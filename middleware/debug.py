import datetime
import socket
import fcntl
import struct

class ResponseTime(object):
    """Appends response header X-Response-Time to requests

    This middleware should sit first in the list so that START_TIME
    is evaluated first, and X-Response-Time is calcualted last.
    """
    def process_request(self, request):
        request.META['START_TIME'] = datetime.datetime.now()
    
    def process_response(self, request, response):
        current_time = datetime.datetime.now()
        old_time = request.META['START_TIME']
        diff = current_time - old_time
        
        response['X-Response-Time'] = '%dms' % (((diff.seconds*1000000)+diff.microseconds)/1000)
        return response

class ServerIP(object):
    """Appends response header X-Server-IP to requests

    Appends the internal IP address of the server. Useful for debugging
    purposes when used in conjunction with the ResponseTime middleware.
    """
    cached_ips = {}
    
    def get_ip_address(self, ifname):
        if self.cached_ips.has_key(ifname):
            return self.cached_ips[ifname]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.cached_ips[ifname] = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
        except IOError:
            return None
        
        return self.cached_ips[ifname]
        
    def process_response(self, request, response):
        ip = self.get_ip_address('eth1')
        if not ip:
            return response
            
        response['X-Server-IP'] = '%s' % ip
        return response