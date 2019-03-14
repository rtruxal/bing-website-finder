

class CacheManager(object):
    def __init__(self, website_df=None, email_df=None):
        self.website_cache = website_df
        self.email_cache = email_df

