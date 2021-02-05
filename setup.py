from setuptools import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
    'Programming Language :: Python :: 3'
]

setup(
    name='pgn2data',
    version='0.0.1',
    packages=['converter', 'common', 'testing'],
    url='',
    classifiers=classifiers,
    license='GPL2',
    author='Zaid Qureshi',
    author_email='zq99@hotmail.com',
    keywords=['CHESS', 'PGN', 'NOTATION', 'DATA', 'FORSYTH–EDWARDS NOTATION', 'CSV', 'DATASET', 'DATABASE',
              'NORMALIZATION','TABULATION','STRUCTURED DATA'],
    install_requires=[
        'chess'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    description='Transforms a chess pgn file into a csv dataset containing game information and move information',
)
