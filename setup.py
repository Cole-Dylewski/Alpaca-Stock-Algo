from setuptools import setup, find_packages


setup(
    name='alpaca-historical-extract',
    version='1.3.0',
    license='MIT',
    description='README.md',
    long_description=open('README.md').read(),
    author="Cole Dylewski",
    author_email='cole.dylewski@gmail.com',
    url='https://github.com/Cole-Dylewski/Alpaca-Stock-Algo',
    keywords='Alpaca Stock Extraction',
    include_package_data=False,
    packages=['alpaca-historical-extract'],
    package_dir={'alpaca-historical-extract':'src/alpaca-historical-extract'},
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