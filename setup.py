from setuptools import setup

requires = open("requirements.txt").read().strip().split("\n")
dev_requires = open("dev-requirements.txt").read().strip().split("\n")

setup(
    name='scraper_api',
    install_requires=requires,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = scraper_api.app:main'
        ],
        'console_scripts': [
            'initialize_db = scraper_api.initialize_db:main'
        ],
    },
)
