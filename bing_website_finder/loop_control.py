import pandas as pd
import os
import asyncio
from functools import partial
import sys
assert list(sys.version_info) >= [3, 7], \
    f"This program requires asyncio functionality introduced in Python 3.7.\nYou are currently using Python {sys.version_info.major}.{sys.version_info.minor}"

from bing_website_finder.obj import WebsiteWorker, EmailWorker
from bing_website_finder.io.db_interface import df_to_company_db, email_db_to_df, company_db_to_df, df_to_email_db, get_db







async def _run_job(workers, verbose, testing=False, *, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    tasks = (
        asyncio.ensure_future(
            i.perform_mission(verbose=verbose, testing=testing),
            loop=loop
        ) for i in workers
    )
    await asyncio.gather(*tasks)


def init_shared_email_cache(use_stored=False):
    if use_stored:
        return email_db_to_df()
    cols = ['email', 'company_name', 'person_name', 'person_title']
    df = pd.DataFrame(columns=cols)
    return df


def init_website_workers(num_workers, cache, api_key):
    return (WebsiteWorker(cache, api_key) for i in range(num_workers))

def init_email_workers(num_workers, website_cache, email_cache, api_key):
    return (EmailWorker(website_cache, email_cache, api_key) for i in range(num_workers))


##################################################################################
# Really clumsy initialization functions until I can make a working job-manager.
def _init_all(infilepth, outfilepth, verbose, api_key, num_workers, testing=False):
    assert os.path.exists(infilepth), "Please check the infile path you've specified."
    cache = pd.read_csv(infilepth)
    website_workers = init_website_workers(num_workers, cache, api_key)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run_job(website_workers, verbose, loop=loop))
        df_to_company_db(cache)  # save progress.
        email_cache = init_shared_email_cache(True)
        email_workers = init_email_workers(num_workers, cache, email_cache, api_key)
        loop.run_until_complete(_run_job(email_workers, verbose, testing=testing, loop=loop))
    finally:
        cache.to_csv(outfilepth, index=False)

def _init_emails(infilepth, outfilepth, verbose, api_key, num_workers, resume=False, testing=False):
    if resume:
        website_cache = company_db_to_df()
    else:
        website_cache = pd.read_csv(infilepth)
    email_cache = init_shared_email_cache(use_stored=resume)
    if verbose:
        print('INFO: Datasources initialized')
    email_workers = init_email_workers(num_workers, website_cache, email_cache, api_key)
    loop = asyncio.get_event_loop()
    try:
        if verbose:
            print('INFO: Starting async jobs.')
        loop.run_until_complete(_run_job(email_workers, verbose, testing, loop=loop))
    finally:
        if verbose:
            print('INFO: Ending async jobs.')
        df_to_email_db(email_cache)
        email_cache.to_csv(outfilepth, index=False)

def init(infilepth, outfilepth, operation='all', resume=False, verbose=False, api_key=None, num_workers=5, testing=False):
    if operation == 'all':
        _init_all(infilepth, outfilepth, verbose, api_key, num_workers, testing)
    elif operation == 'emails':
        _init_emails(infilepth, outfilepth, verbose, api_key, num_workers, resume, testing)


if __name__ == "__main__":
    infilepth = os.path.join(__file__, 'data', 'example_input_website_finder.csv')
    outfilepth = os.path.join(__file__, 'data', 'example_output_with_websites.csv')
    init(infilepth, outfilepth, verbose=False, api_key=None)
