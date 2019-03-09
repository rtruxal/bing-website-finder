import sys
from os import path
import requests as r
sys.path[0] = path.realpath('../')

from bing_website_finder.myconfig import MY_ENDPOINT, MY_HEADERS, MY_PARAMS
from bing_website_finder.util import extract_emails, email_query_generator, filter_blacklisted_urls
from bing_website_finder.io.db_interface import read_from_db

class CallAPI():
    
    def __init__(self, q=None, endpoint=None, params=None, headers=None):
        self.current_query = q
        self.search_type = None
        self.session = None
        self.endpoint = endpoint
        self.params = params
        self.headers = headers
        if not self.endpoint:
            self.endpoint = MY_ENDPOINT
        if not self.params:
            self.params = MY_PARAMS.copy()
        if not self.headers:
            self.headers = MY_HEADERS.copy()

    @property
    def _safe_to_call(self):
        if self.session == None:
            return False
        if None in (self.endpoint, self.params, self.headers):
            return False
        if self.session.params['q'] == None:
            return False
        for k,v in self.session.params.items():
            if type(k) != str or type(v) != str:
                return False
        return True

    def _initialize_session(self, search_query):
        session = r.Session()
        session.headers = self.headers
        session.params = self.params
        session.params.update({'q':search_query})
        self.session = session


class CallAPIWeb(CallAPI):
    def __init__(self, q=None, endpoint=None, params=None, headers=None):
        super(CallAPIWeb, self).__init__(
            q=q, endpoint=endpoint, params=params, headers=headers
            )
        self.search_type = 'web'
        self.search_filter = 'webPages'

    def call_bing(self, query_override=None, pass_on_failure=False):
        # use the other function to assign a pretend browser to self.session.
        if query_override is not None:
            self._initialize_session(query_override)
        else:
            self._initialize_session(self.current_query)
        # use the .get(<some_url>) function to call the API
        response = self.session.get(self.endpoint)
        # return the response data if the call was successful. Handle error if not.
        if response.status_code == 200:
            return response.json()
        else:
            print('API RETURNED {}'.format(response.status_code))
            if pass_on_failure:
                pass
            else:
                return dict()

    def get_urls_from_result(self, JSON, get_item=None):
        _items = get_item
        if not _items:
            _items = self.search_filter
        return (i['url'] for i in JSON[_items]['value'])

def check_db():
    sql = "SELECT * FROM companies;"
    companies = read_from_db(sql)
    for i in companies:
        [print(j) for j in i]
        print()


if __name__ == "__main__":
    # adapter = CallAPIWeb('tom cruise')
    # print(adapter._safe_to_call)
    # res = adapter.call_bing()
    # print(adapter._safe_to_call)
    # print(res)
    # print(sys.path)
    check_db()