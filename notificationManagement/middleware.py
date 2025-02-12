# middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFOnWebSocket(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/ws/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
