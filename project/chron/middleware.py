class IPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        ip = response.META["X-Forwarded-For"]
        print(ip)
        return self.get_response(request)