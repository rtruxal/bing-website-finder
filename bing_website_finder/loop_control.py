import pandas as pd
import os
import asyncio
import sys
assert list(sys.version_info) >= [3, 7], \
    f"This program requires asyncio functionality introduced in Python 3.7.\nYou are currently using Python {sys.version_info.major}.{sys.version_info.minor}"

from bing_website_finder.obj import WebsiteWorker, EmailWorker
from bing_website_finder.io.db_interface import df_to_company_db



async def _execute_website_workers(workers, verbose, *, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    tasks = (
        asyncio.ensure_future(
            i.perform_mission(verbose=verbose),
            loop=loop
        ) for i in workers
    )
    await asyncio.gather(*tasks)

async def _execute_email_workers(workers, verbose, *, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    tasks = (
        asyncio.ensure_future(
            i.perform_mission(verbose=verbose),
            loop=loop
        ) for i in workers
    )
    await asyncio.gather(*tasks)

def init_website_job(num_workers, cache, api_key):
    return (WebsiteWorker(cache, api_key) for i in range(num_workers))

def init_email_job(num_workers, cache, api_key):
    return (EmailWorker(cache, api_key) for i in range(num_workers))

def init(infilepth, outfilepth, operations='all', verbose=False, api_key=None, num_workers=5):
    assert os.path.exists(infilepth), "Please check the infile path you've specified."
    cache = pd.read_csv(infilepth)
    website_workers = init_website_job(num_workers, cache, api_key)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_execute_website_workers(website_workers, verbose, loop=loop))
        df_to_company_db(cache) # save progress.
        email_workers = init_email_job(num_workers, cache, api_key)
        loop.run_until_complete(_execute_email_workers(email_workers, verbose, loop=loop))
    finally:
        cache.to_csv(outfilepth, index=False)


if __name__ == "__main__":
    infilepth = os.path.join(__file__, 'data', 'example_input_website_finder.csv')
    outfilepth = os.path.join(__file__, 'data', 'example_output_with_websites.csv')
    init(infilepth, outfilepth, verbose=False, api_key=None)
