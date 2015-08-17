try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'collect data with automated hardware power cycling',
    'author': 'Nathan Harrington',
    'url': 'https://github.com/nharringtonwasatch/BoardTester',
    'download_url': 'https://github.com/nharringtonwasatch/BoardTester',
    'author_email': 'nharrington@wasatchphotonics.com',
    'version': '1.0.0',
    'install_requires': ['phidgeter', 'wasatchusb', 'wpexam',
                         'colorama'],
    'packages': ['boardtester'],
    'scripts': [],
    'name': 'BoardTester'
}

setup(**config)
