from setuptools import setup, find_packages
import sys


setup(name="bing_website_finder",
      version='0.0.1',

      description='See README.md',

      url='https://please.buythingsfrom.us',
      author='Robert Truxal',
      author_email='rtruxal2020@outlook.com',
      license='MIT-like (see LICENCE file)',

      packages=find_packages(),

      include_package_data=True,
      package_dir={'data' : 'bing_website_finder/data'},
      package_data={'data' : ['data/*.csv']},

      entry_points={
        'console_scripts' : [
            'bwf = bing_website_finder.__main__:main',
            'bing_website_finder = bing_website_finder.__main__:main',
        ]
      },

      zipsafe=False,

      python_requires='>=3.7.0',
      install_requires= [
          'aiohttp',
          'pandas'
      ]
    )
