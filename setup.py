# -*- coding: utf-8 -*-

import codecs
from distutils.core import setup

setup(name='sparqlprotocolproxy',
      version='0.1',
      description='Small SPARQL protocol proxy server',
      long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
      license='New BSD',
      author='Christoph Burgmer',
      author_email="cburgmer@ira.uka.de",
      url = 'http://github.com/cburmer/sparqlprotocolproxy',
      py_modules=['sparqlprotocolproxy'],
      requires=['SuRF'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'Python SPARQL HTTP',
)
