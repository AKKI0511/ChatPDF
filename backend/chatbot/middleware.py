from django.utils.deprecation import MiddlewareMixin

class XFrameOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/media/'):
            response['X-Frame-Options'] = 'ALLOW-FROM http://127.0.0.1:3000'  # Or the URL of your frontend
        return response
