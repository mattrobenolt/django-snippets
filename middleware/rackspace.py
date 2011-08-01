class SetRemoteAddrFromForwardedFor(object):
    """Support for REMOTE_ADDR when using Rackspace's Cloud Load Balancer.

    Rackspace Cloud Load Balancer appends the real IP in the request header:
        X-Cluster-Client-IP
    """
    def process_request(self, request):
        try:
            # Rackspace Cloud uses X-Cluster-Client-IP header instead of X-Forwarded-For
            real_ip = request.META['HTTP_X_CLUSTER_CLIENT_IP']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip