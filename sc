#! /usr/bin/env python

import re
import os

import sharedcache
from sharedcache import loaders

def _selectDirectory( candidates, filename, requiredSpace ):
  # check if some repository file already exists
  for c in candidates:
    if os.path.isfile( os.path.join( c, filename ) ):
      return c

  if requiredSpace <= 0: return candidates[0]

  # look for a good place where to put repository
  for c in candidates:
    stat = os.statvfs( c )
    av = stat.f_bsize * stat.f_bfree
    if av >= requiredSpace:
      return c

  return None

def _parseSize( s ):
  B = 1
  kB = 1000
  MB = 1000 * 1000
  GB = 1000 * 1000 * 1000
  units = {"B":B, "kB":kB, "MB":MB, "GB":GB,
           "k":kB, "M":MB, "G":GB}

  pat = "^(?P<size>[0-9]+)(?P<unit>(B|kB|MB|GB|k|M|G)?)$"
  reg = re.compile( pat )

  m = reg.match( s )
  if not m: return None

  unit = 1
  if m.group( "unit" ) != "": unit = units[m.group( "unit" )]
  return int( int( m.group( "size" ) ) * unit )

if __name__ == "__main__":
  import sys
  from optparse import OptionParser

  parser = OptionParser()
  parser.add_option( "-f", "--file", dest = "filename", default = "repofile",
                     help = "write repofile status to FILE", metavar = "FILE" )
  parser.add_option( "-d", "--directories", dest = "directories", default = "/tmp:/var/tmp",
                     help = "select repository directory from colon separated DIRLIST", metavar = "DIRLIST" )
  parser.add_option( "-s", "--size", dest = "size", default = "0", type = "string",
                     help = "repository estimated size" )
  parser.add_option( "-n", "--name", dest = "name", default = "", type = "string", metavar = "NAME",
                     help = "repository name. Will install repository file and loader output to <repository-directory>/NAME/" )

  parser.add_option( "--use", dest = "use", default = False, action = "store_true",
                     help = "register a use of the repository" )
  parser.add_option( "--unuse", dest = "unuse", default = False, action = "store_true",
                     help = "unregister a use of the repository" )
  parser.add_option( "--location", dest = "location", default = False, action = "store_true",
                     help = "print location of existing repository" )

  ( options, args ) = parser.parse_args()

  dirs = options.directories.split( ':' )
  req = _parseSize( options.size )
  repoBase = _selectDirectory( dirs, options.filename, req )
  if repoBase is None:
    sys.stderr.write( "ERROR: Could not find a place to put repository in directory list \"%s\"\n" % options.directories )
    sys.exit( -1 )

  repoDirectory = os.path.normpath( os.path.join( repoBase, options.name ) )
  if not os.path.isdir( repoDirectory ):
    os.mkdir( repoDirectory )

  l = loaders.EmptyLoader()
  for arg in args:
    splitted = arg.split( ':', 1 )
    class_ = splitted[0]
    argument = None
    if len( splitted ) > 1:
      argument = splitted[1]

    if class_ == "http":
      l = loaders.HttpLoader( argument, destinationDir = repoDirectory )
    elif class_ == "dirac":
      l = loaders.DiracLoader( argument, destinationDir = repoDirectory )
    elif class_ == "md5":
      l = loaders.ChecksumLoaderDecorator( l, hexdigest = argument )
    elif class_ == "tar":
      l = loaders.TarfileLoaderDecorator( l, destinationDir = repoDirectory )
    elif class_ == "dummy":
      l = loaders.DummyLoaderDecorator( l )
    else:
      print "unknown loader class: %s" % class_
      sys.exit( -1 )

  repo = sharedcache.Repo( os.path.join( repoDirectory, options.filename ), l, os.getppid() )

  ret = True
  if options.use:
    print repo.pid, "try use"
    ret = repo.use()
    print repo.pid, "got use", ret

  if options.unuse:
    ret &= repo.unuse( rmdir = options.name != "" )
    print repo.pid, "ok", ret

  if not ret:
    sys.exit( -1 )

  if options.location:
    print repoDirectory
