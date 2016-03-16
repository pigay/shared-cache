import loader
import hashlib

__all__ = ['ChecksumLoaderDecorator']

class ChecksumLoaderDecorator( loader.LoaderDecorator ):
  def __init__( self, loader, hexdigest ):
    super( ChecksumLoaderDecorator, self ).__init__( loader )
    self.hexdigest = hexdigest

  def postLoad( self, state ):
    if state == self.states.OK:
      md5 = hashlib.md5()
      for path in self.loader.pathList():
        f = open( path, 'r' )
        md5.update( f.read() )
        f.close()
      state = self.states.BROKEN
      if md5.hexdigest() == self.hexdigest:
        state = self.states.OK

    return state

