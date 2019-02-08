import asyncio
lock = asyncio.Lock()
from math import isnan

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
