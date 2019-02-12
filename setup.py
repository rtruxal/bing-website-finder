from setuptools import setup, find_packages
import sys

with open('README.md', 'r') as infile:
    long_descr = infile.read()

setup(name="bing_website_finder",
      version='0.0.1',

      description='Add websites to a list of companies from the commandline.',
      long_description=long_descr,
      url='https://please.buythingsfrom.us',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3 :: Only',
          'Environment :: Console',
          'Framework :: AsyncIO',
          'Natural Language :: English',
          'Natural Language :: Esperanto',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: Name Service (DNS)',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
          'Topic :: Internet :: WWW/HTTP :: Site Management',
          'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
      ],
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
      ],
    )
