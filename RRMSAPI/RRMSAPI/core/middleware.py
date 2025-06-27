from datetime import datetime
import logging
import json

logger = logging.getLogger('drf_logger')

class DRFLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_body = self.get_request_body(request)
        response = self.get_response(request)
        response_body = self.get_response_body(response)

        logger.info(json.dumps({
            'timestamp': str(datetime.now()),
            'method': request.method,
            'path': request.get_full_path(),
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'request_data': request_body,
            'status_code': response.status_code,
            'response_data': response_body,
        }, indent=2, default=str))

        return response

    def get_request_body(self, request):
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                return request.body.decode('utf-8')
        except:
            pass
        return None

    def get_response_body(self, response):
        try:
            if hasattr(response, 'data'):
                return response.data
            return response.content.decode('utf-8')
        except:
            return None