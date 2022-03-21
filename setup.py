from setuptools import setup, find_packages


setup(
    name='Alpaca-Stock-Algo',
    version='1.0.0',
    license='MIT',
    author="Cole Dylewski",
    author_email='cole.dylewski@gmail.com',
    url='https://github.com/Cole-Dylewski/Alpaca-Stock-Algo',
    keywords='Alpaca Stock Extraction',
    include_package_data=True,
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