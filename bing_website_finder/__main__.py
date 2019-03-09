import argparse
import os
import sys
assert list(sys.version_info) >= [3, 7], \
    f"This program requires asyncio functionality introduced in Python 3.7.\nYou are currently using Python {sys.version_info.major}.{sys.version_info.minor}"

from bing_website_finder.loop_control import init
# For testing
from bing_website_finder.myconfig import DEFAULT_SEARCH_API_V7_KEY as default_key
# For production
#from bing_website_finder.config import DEFAULT_SEARCH_API_V7_KEY as default_key

def api_key_checks(cmdline_arg, default_key, verbose):
    if not cmdline_arg:
        if default_key == "CHANGE ME":
            print(
                'ERROR: If you have not updated this package\'s config.py module, you must explicitly specify a bing search API key using the -k option.\n\nExiting.')
            sys.exit(-1)
        if verbose:
            print('WARN: You have not provided an API key via the cmdline. Ensure config.py contains a working key, or bwf will fail silently.')

def main(args=None):
    if not args:
        default_output_file = os.path.join(__file__, 'data', 'bing_website_finder_output.csv')
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action="store_true", help="Increase output verbosity.")
        parser.add_argument('-k', '--api-key', nargs="?", type=str, help="Not optional unless you've changed config.py")
        parser.add_argument('-w', '--num-workers', type=int, default=5, help="Specify the quantity of async workers. Default is 5. Higher numbers increase speed to an extent, but also increase memory usage.")
        parser.add_argument('inpth', nargs=1, type=str, help="Specify an input csv or excel file.")
        parser.add_argument('outpth', default=default_output_file, type=str, help="Specify an output path.")

        arrgs = parser.parse_args()

        api_key = arrgs.api_key
        verbose_flag = arrgs.verbose
        api_key_checks(cmdline_arg=api_key,default_key=default_key, verbose=verbose_flag)

        infilepth = os.path.realpath(*arrgs.inpth)
        outfilepth = os.path.realpath(arrgs.outpth)

        num_workers = arrgs.num_workers
        init(infilepth, outfilepth, verbose=verbose_flag, api_key=api_key, num_workers=num_workers)
    else:
        sys.exit(-1)


if __name__ == "__main__":
    main()
