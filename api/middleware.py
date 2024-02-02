from admin_reorder.middleware import ModelAdminReorder

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

