
_FREE_API_V7_KEY = 'c0468feee246448ca66e2fe9aa940772'
_SEARCH_PATH = 'search?'

_LOCAL_BUSINESS_API_V7_KEY = '637700676f0742e6a688ceeead973fe9'
_LOCAL_BUSINESS_PATH = 'localbusinesses/search?'

_ENTITY_API_V7_KEY = '1a44b1ab1d534379944d6e7278cbaa97'
_ENTITY_PATH = 'entities/search?'



DEFAULT_SEARCH_API_V7_KEY = _FREE_API_V7_KEY
MY_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/' + _SEARCH_PATH



MY_HEADERS = {
    'Ocp-Apim-Subscription-Key' : DEFAULT_SEARCH_API_V7_KEY,
    # 'X-MSEdge-ClientID' : 'CHANGE & UNCOMMENT ME', #<<< Optional.
}

MY_PARAMS = {
    "q" : None,
    "mkt" : "en-US",
    "offset" : "0",
    "responseFilter" : "Webpages",
    "count" : "10"
  }




