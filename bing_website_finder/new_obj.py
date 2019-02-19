from bing_website_finder.config import MY_HEADERS, MY_PARAMS, MY_ENDPOINT

class Worker(object):
    worker_types = {
        'website',
        'email',
    }
    def __init__(self, shared_cache, api_key=None):
        self.shared_cache = shared_cache
        self.company_name = None
        self.worker_type = None

        self.headers = MY_HEADERS.copy()
        if api_key:
            self.headers['Ocp-Apim-Subscription-Key'] = api_key
        self.params = MY_PARAMS.copy()







