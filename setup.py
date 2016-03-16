#!/usr/bin/env python

from distutils.core import setup

setup( name = 'shared-cache',
      version = '0.1',
      description = 'multiple process shared-cache tool',
      author = 'Pierre Gay',
      author_email = 'pierre.gay@u-bordeaux.fr',
#      url = 'http://www',
      packages = ['sharedcache', 'sharedcache.loaders'],
      scripts = ['sc'],
     )
