from math import isnan
import numpy as np
import re
import sys
from typing import Generator
import asyncio
website_cache_lock = asyncio.Lock()
email_cache_lock = asyncio.Lock()

url_blacklist = {
        'N/A',
        'products.office.com',
        'en.wikipedia.org',
        'facebook.com',
        'linkedin.com',
        'bloomberg.com',
        'gnu.org',
    }


async def find_empty_website(cache_record) -> str:
    async with website_cache_lock:
        try:
            for company, website in zip(cache_record['Company Name'], cache_record['Website']):
                if not isinstance(website, str) and isnan(website):
                    cache_record.loc[cache_record['Company Name'] == company,'Website'] = "In Progress"
                    return company
                else:
                    continue
            return 'FINISHED'
        except KeyError as err:
            print(err)
            print('PLEASE CHECK THAT YOUR INPUT CSV HAS THE CORRECT COLUMN NAMES.')
            sys.exit(-1)

async def add_domain_processing_column(cache_record, verbose=False) -> None:
    async with website_cache_lock:
        if 'Domain Selected' not in cache_record.columns:
            cache_record['Domain Selected'] = np.nan
        elif verbose:
            print('INFO: add_domain_processing_column should be executed once before email workers perform their mission.')
        else:
            pass


async def find_empty_domain(cache_record) -> tuple:
    async with website_cache_lock:
        try:
            for company, domain, domain_selected in zip(cache_record['Company Name'], cache_record['Domain'], cache_record['Domain Selected']):
                if isinstance(domain, str) and domain != 'N/A':
                    if not isinstance(domain_selected, str) and isnan(domain_selected):
                        cache_record.loc[cache_record['Company Name'] == company, 'Domain Selected'] = "In Progress"
                        return company, domain
                continue
            return 'FINISHED', 'FINISHED'
        except KeyError as err:
            print(err)
            print('PLEASE CHECK THAT YOUR INPUT DF HAS THE CORRECT COLUMN NAMES.')
            sys.exit(-1)

async def set_website_cache_complete(cache_record, worker, verbose=False) -> None:
    async with website_cache_lock:
        rec = cache_record[cache_record['Company Name'] == worker.company_name]['Domain Selected'].iloc[0]
        if rec == "In Progress":
            cache_record.loc[cache_record['Company Name'] == worker.company_name, 'Domain Selected'] = "DONE"
            if verbose:
                print('INFO: Completed email lookup for {}'.format(worker.company_name))
        else:
            print('Something has gone horribly wrong. Check email output for {}'.format(worker.company_name))


async def ok_to_set_website(cache_record, worker) -> bool:
    async with website_cache_lock:
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


async def set_company_website(cache_record, worker, verbose=False) -> None:
    assert worker.company_name and worker.website
    async with website_cache_lock:
        rec = cache_record[cache_record['Company Name'] == worker.company_name]['Website'].iloc[0]
        if rec == "In Progress":
            cache_record.loc[cache_record['Company Name'] == worker.company_name,'Website'] = worker.website
            cache_record.loc[cache_record['Company Name'] == worker.company_name, 'Domain'] = get_simple_domainname(worker.website)
            if verbose:
                print('successfully saved {} to {}'.format(worker.website, worker.company_name))
        else:
            print('{}\'s website info has already been populated or wasn\'t obtained correctly.'.format(worker.company_name))

#todo: this is a big fucking problem. There is no way to append a df in place, and we can't
async def set_company_emails(email_cache_record, worker, verbose=False) -> None:
    assert worker.domain_name
    add_these = [[i, worker.company_name] for i in worker.unique_emails]
    begin, end = email_cache_record.shape[0], email_cache_record.shape[0] + len(add_these[0])
    async with email_cache_lock:
        for indx, rec in zip(range(begin, end), add_these):
            email_cache_record.loc[indx] = [rec[0], rec[1], None, None]
        if verbose:
            print('INFO: successfully saved emails for {}'.format(worker.company_name))

def strip_http_prefix(url_string) -> str:
    """Uses regex grouping substitution.
    Should return original string if 2nd capturing group doesn't catch."""
    hypertext_prefix_stripper = r'(^https?:\/\/)(.*)'
    return re.sub(hypertext_prefix_stripper, r'\2', url_string)

def get_simple_domainname(url_string, filtering=False) -> str:
    """Uses regex grouping substitution."""
    hypertext_prefix_stripper = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    simple_dn = re.sub(hypertext_prefix_stripper, r'\3', url_string)
    if filtering and _is_blacklisted_url(simple_dn):
        return "N/A"
    return simple_dn


def _is_blacklisted_url(url) -> bool:
    return True if url in url_blacklist else False

def _filter_blacklisted_urls_in_order(urls) -> Generator:
    def _url_blacklist_filter(url):
        return False if url in url_blacklist else True
    for url in urls:
        if _url_blacklist_filter(url):
            yield url
        else:
            yield 'N/A'

def filter_blacklisted_urls(urls, preserve_order=False) -> tuple:
    """
    :param urls: an iterable of website urls.
    :param preserve_order: Setting this to true will take ~1,000x more time but preserve order. Default is False.
    :return: a tuple of filtered urls.
    """
    if preserve_order is False:
        return tuple(set(urls) - url_blacklist)
    else:
        return tuple(_filter_blacklisted_urls_in_order(urls))

def email_query_generator(simple_urls) -> Generator:
    for url in simple_urls:
        if not isinstance(url, str) and isnan(url):
            continue
        elif url == "N/A":
            continue
        yield {'q' : '+"@{}"'.format(url)}

def create_email_query(simple_url) -> str:
    return '+"@{}"'.format(simple_url)

#todo: finish the rest of these.
def adapter_0(findall_result):
    return [i[0] for i in findall_result]
def adapter_1(findall_result):
    return findall_result
def adapter_2(findall_result):
    return findall_result
def adapter_3(findall_result):
    return findall_result
def adapter_4(findall_result):
    return findall_result

def extract_emails(text, finder_number=0, return_all=False) -> list or str:
    adapters = (adapter_0, adapter_1, adapter_2, adapter_3, adapter_4)
    EMAIL_ADDR_FINDERS = (
        r'(\w+[.|\w]\w+(@\w+[.]\w+[.|\w+]\w+))',
        r'(\w+[.|\w])*@(\w+[.])*\w+',
        r'\s([\w-].+@\w.+\.\w+)\s+',
        r'^\W*(\w+-*\w*@\w+\.\w{2,6})\W*',
        r'\W*(\w+-*\w*@\w+\.\w{2,6})\W*$'
    )
    # return_all takes precidence.
    if return_all:
        return [re.findall(regex, text) for regex in EMAIL_ADDR_FINDERS]
    # so it's clear how `finder_number` works:
    assert finder_number in range(len(EMAIL_ADDR_FINDERS))
    regex = EMAIL_ADDR_FINDERS[finder_number]
    # Note that everything in `adapters` must be callable.
    return adapters[finder_number](re.findall(regex, text))

if __name__ == "__main__":
    from os import path as p
    import pandas as pd
    infile = p.join(p.realpath(p.split(__file__)[0]), 'data', 'example_output2.csv')
    try:
        assert p.exists(infile)
    except AssertionError:
        print(infile)
        sys.exit(-1)
    df = pd.read_csv(infile)
    print(df.columns)