
DEFAULT_SEARCH_API_V7_KEY = 'CHANGE ME'

MY_HEADERS = {
    'Ocp-Apim-Subscription-Key' : DEFAULT_SEARCH_API_V7_KEY,
    # 'X-MSEdge-ClientID' : 'CHANGE & UNCOMMENT ME', #<<< Optional.
}

MY_PARAMS = {
    "q" : None,
    "mkt" : "en-US",
    "offset" : "0",
  }

MY_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/search?'