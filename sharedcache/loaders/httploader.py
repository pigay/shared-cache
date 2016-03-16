import loader

import os
import urllib

__all__ = ['HttpLoader']

class HttpLoader( loader.Loader ):
  def __init__( self, url, destinationDir = None, fileName = None ):
    self.url = url
    self.destinationDir = destinationDir or os.getcwd()
    self.destination = os.path.join( self.destinationDir,
                                     fileName or os.path.basename( self.url ) )

  def __call__( self, queue ):
    try:
      queue.put( loader.Loader.states.IN_PROGRESS )
      f = urllib.urlopen( self.url )
      content = f.read()
      f.close()

      f = open( self.destination, "w" )
      f.write( content )
      f.close()
      queue.put( loader.Loader.states.OK )

    except Exception, e:
      print e
      queue.put( loader.Loader.states.BROKEN )

  def delete( self ):
    os.unlink( self.destination )

  def pathList( self ):
    return [self.destination]

