import argparse
import os
import sys
assert list(sys.version_info) >= [3, 7], \
    f"This program requires asyncio functionality introduced in Python 3.7.\nYou are currently using Python {sys.version_info.major}.{sys.version_info.minor}"


TESTING = True


from bing_website_finder.loop_control import init
from bing_website_finder.io.db_interface import db_existance_checks

# For testing
from bing_website_finder.myconfig import DEFAULT_SEARCH_API_V7_KEY as default_key
# For production
#from bing_website_finder.config import DEFAULT_SEARCH_API_V7_KEY as default_key
SUPPORTED_OPERATIONS = {'all', 'emails', 'websites'}

def api_key_checks(cmdline_arg, default_key, verbose):
    if not cmdline_arg:
        if default_key == "CHANGE ME":
            print(
                'ERROR: If you have not updated this package\'s config.py module, you must explicitly specify a bing search API key using the -k option.\n\nExiting.')
            sys.exit(-1)
        if verbose:
            print('WARN: You have not provided an API key via the cmdline. Ensure config.py contains a working key, or bwf will fail silently.')

def cli_arg_checks(parsed_arguments):
    """Raises an error if inconsistencies found. Otherwise, nothing happens."""
    assert parsed_arguments.operation in SUPPORTED_OPERATIONS
    if parsed_arguments.hard and parsed_arguments.operation == 'all':
        raise argparse.ArgumentError('-H can only be used in conjunction with -o.')
    #TODO: flesh out checks & CLI entrypoint structure generally

def main(args=None):
    if not args:
        db_existance_checks()
        default_output_file = os.path.join(__file__, 'data', 'bing_website_finder_output.csv')
        parser = argparse.ArgumentParser()

        parser.add_argument('-v', '--verbose', action="store_true", help="Increase output verbosity.")
        parser.add_argument('-o', '--operation', nargs="?", type=str, default="all", help="Select 'all' or one of the 3 operations: [website|email|profile]")
        parser.add_argument('-H', '--hard', action="store_true", help="Overwrite data in databases. This is the default behavior unless you use the -o arg.")
        parser.add_argument('-k', '--api-key', nargs="?", type=str, help="Not optional unless you've changed config.py")
        parser.add_argument('-w', '--num-workers', type=int, default=5, help="Specify the quantity of async workers. Default is 5. Higher numbers increase speed to an extent, but also increase memory usage.")
        parser.add_argument('inpth', nargs=1, type=str, help="Specify an input csv or excel file.")
        parser.add_argument('outpth', default=default_output_file, type=str, help="Specify an output path.")

        arrgs = parser.parse_args()
        cli_arg_checks(arrgs)

        api_key = arrgs.api_key
        verbose_flag = arrgs.verbose
        api_key_checks(cmdline_arg=api_key,default_key=default_key, verbose=verbose_flag)

        infilepth = os.path.realpath(*arrgs.inpth)
        outfilepth = os.path.realpath(arrgs.outpth)

        operation = arrgs.operation
        resume = not arrgs.hard

        num_workers = arrgs.num_workers

        init(
            infilepth,
            outfilepth,
            verbose=verbose_flag,
            api_key=api_key,
            num_workers=num_workers,
            operation=operation,
            resume=resume,
            testing=TESTING
        )
    else:
        sys.exit(-1)


if __name__ == "__main__":
    main()
