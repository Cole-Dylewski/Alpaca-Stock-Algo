from setuptools import setup, find_packages


setup(
    name='alpaca_historical_extract',
    version='1.18.0',
    license='MIT',
    description='README.md',
    long_description=open('README.md').read(),
    author="Cole Dylewski",
    author_email='cole.dylewski@gmail.com',
    url='https://github.com/Cole-Dylewski/Alpaca-Stock-Algo',
    keywords='Alpaca Stock Extraction',
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={'alpaca_historical_extract':'src/alpaca_historical_extract'},
    install_requires=[
        'pytz',
        'tzdata',
        'pandas-market-calendars',
        'pandas',
        'requests',
        'numpy',
        'alpaca-trade-api',
        'yahoo-fin',
        'yfinance'
      ],

)