#!/usr/bin/env python

from distutils.core import setup

setup( name = 'shared-cache',
      version = '0.2.0',
      description = 'multiple process shared-cache tool',
      author = 'Pierre Gay',
      author_email = 'pierre.gay@u-bordeaux.fr',
      url = 'https://github.com/pigay/shared-cache',
      packages = ['sharedcache', 'sharedcache.loaders'],
      scripts = ['sc'],
     )
