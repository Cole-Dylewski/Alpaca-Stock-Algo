from setuptools import setup, find_packages


setup(
    name='alpaca-historical-extract',
    version='1.0.0',
    license='MIT',
    description='README.md',
    long_description='Generates a series of excel files for all viable stock data in today, yesterday, last week, last month and last year'
                     'Relies on active alapaca account to manage data extraction, works on free data subscription',
    author="Cole Dylewski",
    author_email='cole.dylewski@gmail.com',
    url='https://github.com/Cole-Dylewski/Alpaca-Stock-Algo',
    keywords='Alpaca Stock Extraction',
    include_package_data=False,
    packages=['alapca-historical-extract'],
    package_dir={'alapca-historical-extract':'src/alpaca-historical-extract'},
    install_requires=[
        'pytz',
        'tzdata',
        'pandas-market-calendars',
        'pandas',
        'requests',
        'numpy',
        'alpaca-trade-api',
        'yahoo-fin',
        'yfinance',
      ],

)