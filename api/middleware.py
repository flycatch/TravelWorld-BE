import threading

from admin_reorder.middleware import ModelAdminReorder

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
class ModelAdminReorderWithNav(ModelAdminReorder):
    def process_template_response(self, request, response):
        if response.context_data is not None:
            if 'available_apps' in response.context_data:
                available_apps = response.context_data.get('available_apps')
                response.context_data['app_list'] = available_apps
                response = super().process_template_response(request, response)
                response.context_data['available_apps'] = response.context_data['app_list']
                return response

        # If the conditions above are not met, return the original response
        return response

