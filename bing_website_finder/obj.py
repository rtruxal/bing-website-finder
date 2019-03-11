import asyncio
import aiohttp
import sys
from time import sleep

from bing_website_finder.myconfig import MY_HEADERS, MY_PARAMS, MY_ENDPOINT
from bing_website_finder.util import find_empty_website, ok_to_set_website, set_company_website


class Worker(object):
    worker_types = {
        'website',
        'email',
    }
    def __init__(self, shared_cache, api_key=None):
        self.shared_cache = shared_cache
        try:
            self.loop = asyncio.get_running_loop()
        except:
            self.loop = asyncio.get_event_loop()
        self.company_name = None
        self.worker_type = None

        self.headers = MY_HEADERS.copy()
        if api_key:
            self.headers['Ocp-Apim-Subscription-Key'] = api_key
        self.params = MY_PARAMS.copy()
        self.search_url = MY_ENDPOINT

        self.failed_attempts = 0
        self.mission_complete = False
        # Total estimated matches is garbage.
        #self.tem = 0
        self.increment_offset_by = 0
        self.last_result = None
        self.offset = 0
        self.result_hashes = set()

    def update_offset(self, new_result, subtype='urls'):
        new_items = getattr(new_result, subtype)
        before_adding = len(self.result_hashes)
        self.result_hashes.update((hash(i) for i in new_items))
        after_adding = len(self.result_hashes)
        if after_adding == before_adding:
            self.mission_complete = True
            self.increment_offset_by = -1
        else:
            self.increment_offset_by = len(new_items)
            self.offset += self.increment_offset_by
            self.params['offset'] = self.offset


    def _are_we_done_yet(self, inplace=False):
        if inplace is True:
            self.mission_complete = True if self.company_name == "FINISHED" else False
        else:
            return True if self.company_name == "FINISHED" else False

    async def _call_bing(self):
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get(
                    self.search_url,
                    headers=self.headers,
                    params=self.params
            ) as resp:
                try:
                    assert self.handle_api_response(resp)
                except AssertionError:
                    # return an empty dict to purposefully throw the except: statement in `perform_mission()`
                    return dict()
                return await resp.json()

    def handle_api_response(self, resp):
        """returns True if successful, False if not, and KeyError if the status code isn't in `errors.keys()`."""
        if resp.status == 200:
            return True
        def handle_authentication_error():
            print('ERROR: Your API key is invalid.\nExiting.')
            sys.exit(-1)
        def handle_bad_path_error():
            print("ERROR: Your url endpoint path is invalid or doesn't match your API key.\nExiting.")
            sys.exit(-1)
        def handle_bad_query_error():
            print("WARN: This worker has malformed url parameters & must be reconfigured.\nKilling this worker.")
            self.mission_complete = True
            return False
        def handle_call_quota_error():
            print("WARN: You've hit your call-per-second threshold. Blocking events for 1 second.")
            sleep(1)
            return False
        def handle_server_error():
            print("INFO: Bing is experiencing technical difficulties. Blocking events for 1 second.")
            sleep(1)
            return False
        errors = {
            400 : handle_bad_query_error,
            401 : handle_authentication_error,
            403 : handle_bad_path_error,
            404 : handle_bad_path_error,
            429 : handle_call_quota_error,
            500 : handle_server_error
        }
        return errors[resp.status]()

class EmailWorker(Worker):
    def __init__(self, website_cache, email_cache, api_key=None):
        super(EmailWorker, self).__init__(website_cache, api_key)
        self.email_cache = email_cache
        self.worker_type = 'email'
        self.emails = None

    async def perform_mission(self, verbose=False):
        pass


class WebsiteWorker(Worker):
    def __init__(self, shared_cache, api_key=None):
        super(WebsiteWorker, self).__init__(shared_cache, api_key)
        self.worker_type = 'website'
        self.website = None

    async def perform_mission(self, verbose=False):
        while not self.mission_complete:
            if not self.company_name:
                await self._find_company_name()
                ## THIS IS THE STOP CONDITION.
                if self._are_we_done_yet():
                    if verbose:
                        print('INFO: WebsiteWorker finished. Shutting down.')
                    break
                if verbose:
                    print('INFO: Obtained Company Name')
            if self.company_name and not self.website:
                if verbose:
                    print('INFO: Company Name populated but no website found yet.')
                data = await self._call_bing()
                #######################
                # Maybe this should be its own function
                try:
                    self.website = SearchResultWeb(data).urls[0]
                except KeyError:
                    print('WARN: Results not obtained from Bing for {}.'.format(self.company_name))
                    self.website = "N/A"
                #####################
                if self.website and await ok_to_set_website(self.shared_cache, self):
                    await self._try_set_results()
                    if verbose:
                        print('INFO: Results for {} saved to cache.'.format(self.company_name))
                else:
                    print('WARN: {} worker failed at setting website.'.format(self.company_name))
                    pass
            else:
                print('WARN: {} worker failed at obtaining data from Bing.'.format(self.company_name))
                pass

    async def _find_company_name(self):
        self.company_name = await find_empty_website(self.shared_cache)
        self.params['q'] = self.company_name

    async def _try_set_results(self):
        try:
            await set_company_website(self.shared_cache, self)
            self.company_name = None
            self.website = None
        except KeyError:
            self.failed_attempts += 1
            print('WARN: Failed to get url info for {}.'.format(self.company_name))
            self.website = None

class SearchResultWeb(object):
    def __init__(self, JSON):
        assert '_type' in JSON.keys() and JSON['_type'] == 'SearchResponse', \
            'Hey you can\'t parse that with this.'
        if 'webPages' in JSON.keys():
            self._successful_init(JSON)
        else:
            self._unsuccessful_init()


    def _successful_init(self, JSON):
        self.total_estimated_matches = JSON['webPages']['totalEstimatedMatches']

        self.names = [i['name'] for i in JSON['webPages']['value']]
        self.urls = [j['url'] for j in JSON['webPages']['value']]
        self.snippets = [k['snippet'] for k in JSON['webPages']['value']]
        self.safe_search = [l['isFamilyFriendly'] for l in JSON['webPages']['value']]

        self.display_urls = [n['displayUrl'] for n in JSON['webPages']['value']]

        self.increment_next_offset_by = len(self.names)
        try:
            self.crawl_dates = [m['dateLastCrawled'] for m in JSON['webPages']['value']]
        except KeyError:
            self.crawl_dates = [None for i in self.names]
    def _unsuccessful_init(self):
        self.total_estimated_matches = 0
        self.names = []
        self.urls = []
        self.snippets = []
        self.safe_search = []
        self.display_urls = []
        self.increment_next_offset_by = -1
