import asyncio
import aiohttp
import sys
from time import sleep

from bing_website_finder.config import MY_HEADERS, MY_PARAMS, MY_ENDPOINT
from bing_website_finder.obj.parsers import SearchResultWeb
from bing_website_finder.util import find_empty_website, ok_to_set_website, set_company_website, find_empty_domain, create_email_query, extract_emails, set_website_cache_complete, set_company_emails


class Worker(object):
    worker_types = {
        'website',
        'domain',
        'email',
    }
    def __init__(self, cache_manager, api_key=None):
        self.cache_manager = cache_manager
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

    async def _call_bing(self, verbose=False):
        if verbose:
            print('INFO: calling the API with q={}'.format(self.params['q']))
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
    def __init__(self, cache_manager, api_key=None, max_email_searches=3):
        super(EmailWorker, self).__init__(cache_manager, api_key)
        self.worker_type = 'email'

        self.max_searches_per_suffix = max_email_searches
        self.searches_performed = 0
        self.resp_snips = []
        self.unique_emails = set()

        self.domain_name = None

    async def perform_mission(self, verbose=False, testing=False):
        while not self.mission_complete:
            if not self.company_name:
                await self._find_company_name(verbose=verbose)
                if self._are_we_done_yet():
                    if verbose:
                        print('INFO: EmailWorker finished. Shutting down.')
                        break
                else:
                    if verbose:
                        print('INFO: Worker got False from ._are_we_done_yet()')
                    #TODO: placeholder for pagination loop
                    #todo: use self.update_offset() declared above.
                    data = await self._call_bing(verbose=verbose)
                    #todo: endtodo
                    try:
                        self.resp_snips = SearchResultWeb(data).snippets
                        if len(self.resp_snips) == 0:
                            raise KeyError()
                    except KeyError:
                        print('WARN: Results not obtained from Bing for {}.'.format(self.company_name))
                    except AssertionError:
                        print('WARN: Bing returned JSON for {} but it is incomplete or malformed. Bypassing.'.format(self.params['q']))
                        if verbose:
                            print('INFO: JSON dump from bing - ')
                            print(data)
                        self.reset()
                        continue
                    if len(self.resp_snips) > 0:
                        await self.iter_find_emails(verbose=verbose, testing=testing)
                        await self._try_set_cache_data(verbose=verbose)
                    else:
                        print('WARN: worker failed at obtaining snips.')

    def reset(self):
        self.searches_performed = 0
        self.resp_snips = []
        self.unique_emails = set()
        self.company_name = None
        self.domain_name = None

    async def _try_set_cache_data(self, verbose=False):
        try:
            self.cache_manager.email_cache = await set_company_emails(self.cache_manager.email_cache, self, verbose=verbose)
            await set_website_cache_complete(self.cache_manager.website_cache, self, verbose=verbose)
        finally:
            self.reset()

    async def _find_company_name(self, verbose=False):
        if verbose:
            print('INFO: email_worker finding company name from cache.')
        self.company_name, self.domain_name = await find_empty_domain(self.cache_manager.website_cache)
        self.params['q'] = create_email_query(self.domain_name)
        if verbose:
            print('INFO: Domain {} selected.'.format(self.domain_name))


    async def iter_find_emails(self, verbose=False, testing=False):
        if verbose:
            print('INFO: email_worker.iter_find_emails() triggered.')
        for snip in self.resp_snips:
            if testing:
                await asyncio.sleep(0)
                self.unique_emails.update(extract_emails(snip))
            else:
                for finder in range(5):
                    await asyncio.sleep(0)
                    self.unique_emails.update(extract_emails(snip, finder))

        if verbose and len(self.unique_emails) > 0:
            print('INFO: emails for {} obtained'.format(self.company_name))
        elif verbose:
            print('INFO: no emails for {} obtained'.format(self.company_name))

class WebsiteWorker(Worker):
    def __init__(self, cache_manager, api_key=None):
        super(WebsiteWorker, self).__init__(cache_manager, api_key)
        self.worker_type = 'website'
        self.website = None

    async def perform_mission(self, verbose=False, testing=False):
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
                if self.website and await ok_to_set_website(self.cache_manager.website_cache, self):
                    await self._try_set_results(verbose=verbose)
                    if verbose:
                        print('INFO: Results for {} saved to cache.'.format(self.company_name))
                else:
                    print('WARN: {} worker failed at setting website.'.format(self.company_name))
                    pass
            else:
                print('WARN: {} worker failed at obtaining data from Bing.'.format(self.company_name))
                pass

    async def _find_company_name(self):
        self.company_name = await find_empty_website(self.cache_manager.website_cache)
        self.params['q'] = self.company_name

    async def _try_set_results(self, verbose=False):
        try:
            await set_company_website(self.cache_manager.website_cache, self, verbose=verbose)
            self.company_name = None
            self.website = None
        except KeyError:
            self.failed_attempts += 1
            print('WARN: Failed to get url info for {}.'.format(self.company_name))
            self.website = None

