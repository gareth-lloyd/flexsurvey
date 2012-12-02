# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='flexsurvey',
    version='0.0.1',
    author=u'Gareth Lloyd',
    author_email='glloyd@gmail.com',
    packages=find_packages(),
    url='https://github.com/gareth-lloyd/flexsurvey',
    license='BSD licence, see LICENCE.txt',
    description='Create flexible surveys in Django',
    long_description=open('README.txt').read(),
    include_package_data=True,
)
