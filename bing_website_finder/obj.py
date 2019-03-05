import aiohttp
from bing_website_finder.config import MY_HEADERS, MY_PARAMS, MY_ENDPOINT
from bing_website_finder.util import find_empty_website, ok_to_set_website, set_company_website

class SearchResultWeb(object):
    def __init__(self, JSON):
        assert JSON['_type'] == 'SearchResponse', \
            'Hey you can\'t parse that with this.'
        self.query = JSON['queryContext']['originalQuery']
        self.total_estimated_matches = JSON['webPages']['totalEstimatedMatches']

        self.names = [i['name'] for i in JSON['webPages']['value']]
        self.urls = [j['url'] for j in JSON['webPages']['value']]
        self.snippets = [k['snippet'] for k in JSON['webPages']['value']]
        self.safe_search = [l['isFamilyFriendly'] for l in JSON['webPages']['value']]
        self.crawl_dates = [m['dateLastCrawled'] for m in JSON['webPages']['value']]
        self.display_urls = [n['displayUrl'] for n in JSON['webPages']['value']]

        self.increment_next_offset_by = len(self.urls)


class WebsiteWorker(object):
    def __init__(self, shared_cache, api_key=None):
        self.shared_cache = shared_cache
        self.company_name = None
        self.website = None

        self.headers = MY_HEADERS.copy()
        if api_key:
            self.headers['Ocp-Apim-Subscription-Key'] = api_key
        self.params = MY_PARAMS.copy()
        self.search_url = MY_ENDPOINT

        self.failed_attempts = 0
        self.mission_complete = False

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
                    assert resp.status == 200
                except AssertionError:
                    # return an empty dict to purposefully throw the except: statement in `perform_mission()`
                    return dict()
                return await resp.json()

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


##TODO: FINISH THIS
class EmailWorker(object):
    def __init__(self, shared_cache, api_key=None):
        self.shared_cache = shared_cache
        self.company_name = None
        #TODO: SWAP OUT WEBSITE WITH EMAILS
        self.website = None

        self.headers = MY_HEADERS.copy()
        if api_key:
            self.headers['Ocp-Apim-Subscription-Key'] = api_key
        self.params = MY_PARAMS.copy()
        self.search_url = MY_ENDPOINT

        self.failed_attempts = 0
        self.mission_complete = False

    async def _find_company_name(self):
        self.company_name = await find_empty_website(self.shared_cache)
        self.params['q'] = self.company_name

    async def _call_bing(self):
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get(
                    self.search_url,
                    headers=self.headers,
                    params=self.params
            ) as resp:
                try:
                    assert resp.status == 200
                except AssertionError:
                    # return an empty dict to purposefully throw the except: statement in `perform_mission()`
                    return dict()
                return await resp.json()
    #TODO: FIGURE OUT HOW TO FIND EMAILS FROM SEARCH RESULTS.


if __name__ == "__main__":
    pass
