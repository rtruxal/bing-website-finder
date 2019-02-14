Bing Website Finder (`bwf`)
===================
--------------------------

## Purpose:
`bing_website_finder` (aka `bwf`) finds websites for an arbitrarily long list of company names.
It does this using an `asyncio` event loop, and is therefore both exceptionally fast & requires `>=` python3.7

<br>

## Requirements:
 - Python >= 3.7
 - A Bing Search API subscription
 - A CSV full of company names

<br>

## Installation:

#### From pypi:
```sh
$ pip install bwf
```

#### Direct download:
From the commandline run:
```sh
$ git clone https://github.com/rtruxal/company-website-finder.git
$ cd bing-website-finder/
$ pip install .
```

#### Without installing (python API):
```sh
$ git clone https://github.com/rtruxal/company-website-finder.git
$ cd bing-website-finder/
$ python --version `#check your python version to make sure it's >=3.7`
Python 3.7.2
$ python `#start python`
Python 3.7.2 (default, Jan  2 2119, 17:17:17) [MSC v.1111 2222 bit (DAM46)] :: Anaconda, Inc. on win3333
Type "help", "copyright", "credits" or "license" for more information.
```
And then:
```py
>>> from bing_website_finder.get_websites import init
>>> from os import path
>>>
>>> infile = path.realpath('./bing_website_finder/data/example_input_website_finder.csv')
>>> outfile = path.realpath('./results.csv')
>>> bing_api_key = '987654321deadbeef123456789'
>>>
>>> init(infile, outfile, verbose=False, api_key=bing_api_key)

```



<br>

## Configuration & Usage:

### STEP 1:
#### Create a CSV input file
The easiest way to glean the input format is by checking out `bing_website_finder/data/example_input_website_finder.csv` (which was gathered from [a very old SEC website](https://www.sec.gov/rules/other/4-460list.htm)) for a practical example.  

Your input CSV **must** include the following 2 columns (case sensitive):
 - Company Name
 - Website  


### STEP 2:
#### Permenantly store a Bing Search API Key in `config.py`
Locate the `bing_website_finder/config.py` file & modify this line:
```py
DEFAULT_SEARCH_API_V7_KEY = 'CHANGE ME'
```

### STEP 3:
**IMPORTANT NOTE: `bwf` will fail silently if you do not change `api_key=none` nor modify : `DEFAULT_SEARCH_API_V7_KEY` inside of `config.py`**

#### Python usage:
You can find the primary interface inside of `bing_website_finder/get_websites.py`.  
It's called `init()`. Here is it's declaration as of v0.0.1:
```py
def init(infilepth, outfilepth, verbose=False, api_key=None, num_workers=5):
    assert os.path.exists(infilepth), "Please check the infile path you've specified."
    cache = pd.read_csv(infilepth)
    workers = (Worker(cache, api_key) for i in range(num_workers))
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_execute(workers, verbose, loop=loop))
    finally:
        cache.to_csv(outfilepth, index=False)
```
If you do not specify an `api_key` argument, the `DEFAULT_SEARCH_API_V7_KEY` variable in `bing_website_finder/config.py` will be used.


#### cmdline usage:
Insallation via pip automatically creates an executable and places it in your $PYTHONPATH. 

If `/YOUR/PYTHON/ENV/bin`* is in your `$PATH`**, simply type:
```sh
$ bwf --help
```
or
```sh
$ bing_website_finder --help
```  
if neither of these^ work after installation, you can always use:  

```sh
$ python -m bwf --help
```
or
```sh
$ python -m bing_website_finder --help
```
\* - (`/YOUR/PYTHON/ENV/Scripts` on Windows)  
\** - (`%PATH%` on Windows)

