import pandas as pd
import os
import asyncio
import sys
assert list(sys.version_info) >= [3, 7], \
    f"This program requires asyncio functionality introduced in Python 3.7.\nYou are currently using Python {sys.version_info.major}.{sys.version_info.minor}"


from bing_website_finder.obj import Worker

async def _execute(workers, verbose, *, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    tasks = (asyncio.ensure_future(i.perform_mission(verbose=verbose), loop=loop) for i in workers)
    await asyncio.gather(*tasks)

def init(infilepth, outfilepth, verbose=False, api_key=None, num_workers=5):
    assert os.path.exists(infilepth), "Please check the infile path you've specified."
    cache = pd.read_csv(infilepth)
    workers = (Worker(cache, api_key) for i in range(num_workers))
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_execute(workers, verbose, loop=loop))
    finally:
        cache.to_csv(outfilepth, index=False)



if __name__ == "__main__":
    infilepth = os.path.join(__file__, 'data', 'example_input_website_finder.csv')
    outfilepth = os.path.join(__file__, 'data', 'example_output_with_websites.csv')
    init(infilepth, outfilepth, verbose=False, api_key=None)
