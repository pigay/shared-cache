import loader

import os
import tarfile as tf

__all__ = ['TarfileLoaderDecorator']

class TarfileLoaderDecorator( loader.LoaderDecorator ):
  def __init__( self, loader, destinationDir = None ):
    super( TarfileLoaderDecorator, self ).__init__( loader )
    self.destinationDir = destinationDir
    self.listDict = {}
    for tar in self.loader.pathList():
      self.listDict[tar] = tar + ".list"

  def postLoad( self, state ):
    if state == self.states.OK:
      for tar in self.loader.pathList():
        filelist = self.listDict[tar]
        t = tf.open( tar )
        t.extractall( self.destinationDir )
        f = open( filelist, 'w' )

        for ff in t.getnames():
          f.write( ff + '\n' )
          print "archive content", ff

        f.close()
        t.close()

    return state

  def preDelete( self ):
    print "TarfileLoaderDecorator preDelete", self.listDict
    for filelist in self.listDict.values():
      directories = []
      f = open( filelist, 'r' )
      for ff in f.readlines():
        ff = os.path.join( self.destinationDir, ff.strip() )
        if os.path.isdir( ff ):
          directories.append( ff )
        else:
          os.unlink( ff )
          print "delete file", ff

      f.close()
      os.unlink( filelist )

      directories.sort()
      directories.reverse()

      for d in directories:
        os.rmdir( d )
        print "delete directory", d

