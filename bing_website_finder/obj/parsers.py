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