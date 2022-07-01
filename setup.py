from setuptools import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
]

setup(
    name='pgn2data',
    version='0.0.6',
    packages=['converter', 'common', 'testing'],
    url='',
    classifiers=classifiers,
    license='GPL-3.0+',
    author='zq99',
    author_email='zq99@hotmail.com',
    keywords=['CHESS', 'PGN', 'NOTATION', 'DATA', 'FORSYTH–EDWARDS NOTATION', 'CSV', 'DATASET', 'DATABASE',
              'NORMALIZATION', 'TABULATION', 'STRUCTURED DATA'],
    install_requires=[
        'chess'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    description='Converts a chess pgn file into a csv dataset containing game information and move information',
)
