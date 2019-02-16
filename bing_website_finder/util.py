import asyncio
lock = asyncio.Lock()
from math import isnan
import re

url_blacklist = {
        'N/A',
        'products.office.com',
        'en.wikipedia.org',
        'facebook.com',
        'linkedin.com',
        'bloomberg.com',
        'gnu.org',
    }


async def find_empty_website(cache_record):
    async with lock:
        for company, website in zip(cache_record['Company Name'], cache_record['Website']):
            if not isinstance(website, str) and isnan(website):
                cache_record.loc[cache_record['Company Name'] == company,'Website'] = "In Progress"
                return company
            else:
                continue
        return 'FINISHED'


async def ok_to_set_website(cache_record, worker):
    async with lock:
        print(worker.company_name)
        rec = cache_record[cache_record['Company Name'] == worker.company_name]['Website'].iloc[0]
        if rec == "In Progress":
            # print('{} is in progress'.format(worker.company_name))
            return True
        elif not isinstance(rec, str) and isnan(rec):
            print('{} has not been checked out'.format(worker.company_name))
            return False
        else:
            print('Website for {} already placed.'.format(worker.company_name))
            return False


async def set_company_website(cache_record, worker):
    assert worker.company_name and worker.website
    async with lock:
        rec = cache_record[cache_record['Company Name'] == worker.company_name]['Website'].iloc[0]
        if rec == "In Progress":
            cache_record.loc[cache_record['Company Name'] == worker.company_name,'Website'] = worker.website
            print('successfully saved {} to {}'.format(worker.website, worker.company_name))
        else:
            print('{}\'s website info has already been populated or wasn\'t obtained correctly.'.format(worker.company_name))

##TODO: FINISH THESE
async def find_empty_email(cache_record):
    async with lock:
        for company, emails in zip(cache_record['Company Name'], cache_record['Emails']):
            if not isinstance(emails, str) and isnan(emails):
                cache_record.loc[cache_record['Company Name'] == company,'Emails'] = "In Progress"
                return company
            else:
                continue
        return 'FINISHED'


def strip_http_prefix(url_string):
    """Uses regex grouping substitution.
    Should return original string if 2nd capturing group doesn't catch."""
    hypertext_prefix_stripper = r'(^https?:\/\/)(.*)'
    return re.sub(hypertext_prefix_stripper, r'\2', url_string)

def get_simple_domainname(url_string):
    """Uses regex grouping substitution."""
    hypertext_prefix_stripper = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    return re.sub(hypertext_prefix_stripper, r'\3', url_string)



def _filter_blacklisted_urls_in_order(urls):
    def _url_blacklist_filter(url):
        return False if url in url_blacklist else True
    for url in urls:
        if _url_blacklist_filter(url):
            yield url
        else:
            yield 'N/A'

def filter_blacklisted_urls(urls, preserve_order=False):
    """
    :param urls: an iterable of website urls.
    :param preserve_order: Setting this to true will take ~1,000x more time but preserve order. Default is False.
    :return: a tuple of filtered urls.
    """
    if preserve_order is False:
        return tuple(set(urls) - url_blacklist)
    else:
        return tuple(_filter_blacklisted_urls_in_order(urls))

def email_query_generator(simple_urls):
    for url in simple_urls:
        if not isinstance(url, str) and isnan(url):
            pass
        yield {'q' : '+"@{}"'.format(url)}
