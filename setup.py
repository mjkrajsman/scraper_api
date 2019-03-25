from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'waitress',
    'typing',
    'requests',
    'bs4',
    'pyramid_tm',
    'sqlalchemy',
    'zope.sqlalchemy',
    'simplejson'
]

dev_requires = [
    'pyramid_debugtoolbar',
    'pytest',
    'webtest'
]

setup(
    name='scraper_api',
    install_requires=requires,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = scraper_api:main'
        ],
        'console_scripts': [
            'initialize_db = scraper_api.initialize_db:main'
        ],
    },
)
