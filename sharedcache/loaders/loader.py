import time
import multiprocessing
import Queue

__all__ = ['Enum', 'Loader', 'EmptyLoader', 'LoaderDecorator', 'DummyLoaderDecorator', 'LoaderComposite', 'LoaderProcess']

class Enum( set ):
    def __getattr__( self, name ):
        if name in self:
            return name
        raise AttributeError

class Loader( object ):
  states = Enum( ["UNKNOWN", "IN_PROGRESS", "BROKEN", "OK"] )
  terminalStates = Enum( [states.OK, states.BROKEN] )
  badStates = Enum( [states.UNKNOWN, states.BROKEN] )
  def __call__( self, queue ):
    raise NotImplementedError

  def delete( self ):
    raise NotImplementedError

  def pathList( self ):
    return []

class EmptyLoader( Loader ):
  def __call__( self, queue ):
    queue.put( Loader.states.IN_PROGRESS )
    time.sleep( 1 )
    queue.put( Loader.states.OK )

  def delete( self ):
    pass

class LoaderDecorator( Loader ):
  def __init__( self, loader ):
    self.loader = loader

  def preLoad( self ):
    pass

  def postLoad( self, state ):
    return state

  def preDelete( self ):
    pass
  def postDelete( self ):
    pass

  def __call__( self, queue ):
    self.preLoad()

    loaderQueue = multiprocessing.Queue()
    self.loader( loaderQueue )

    loaderState = self.states.UNKNOWN
    while loaderState not in self.terminalStates:
      queue.put( loaderState )
      try:
        loaderState = loaderQueue.get( block = True, timeout = 1 )
      except Queue.Empty:
        pass

    state = self.postLoad( loaderState )
    if state not in self.states: state = self.states.BROKEN
    queue.put( state )

  def delete( self ):
    self.preDelete()
    self.loader.delete()
    self.postDelete()

  def pathList( self ):
    return self.loader.pathList()

class DummyLoaderDecorator( LoaderDecorator ):
  def preLoad( self ):
    print "DummyLoaderDecorator preLoad", self.pathList()
  def postLoad( self, state ):
    print "DummyLoaderDecorator postLoad", state
    return state

  def preDelete( self ):
    print "DummyLoaderDecorator preDelete"
  def postDelete( self ):
    print "DummyLoaderDecorator postDelete"

class LoaderComposite( Loader ):
  def __init__( self, loaders = [] ):
    self.loaders = loaders

  def __call__( self, queue ):
    loaderQueue = multiprocessing.Queue()
    state = self.states.OK

    queue.put( self.states.IN_PROGRESS )

    for loader in self.loaders:
      loader( loaderQueue )

      loaderState = self.states.UNKNOWN
      while loaderState not in self.terminalStates:
        queue.put( loaderState )
        try:
          loaderState = loaderQueue.get( block = True, timeout = 1 )
        except Queue.Empty:
          pass

      if loaderState != self.states.OK:
        state = loaderState

    queue.put( state )

  def delete( self ):
    for loader in self.loaders:
      loader.delete()

  def pathList( self ):
    ret = []
    for loader in self.loaders:
      ret += loader.pathList()

    return ret

class LoaderProcess( object ):
  def __init__( self, loader ):
    self.loader = loader
    self.queue = multiprocessing.Queue()
    self.process = multiprocessing.Process( target = loader, args = ( self.queue, ) )
    self.state = Loader.states.UNKNOWN

  def start( self ):
    self.process.start()

  def join( self ):
    self.getState()
    self.process.join()

  def getState( self ):
    while not self.queue.empty():
      self.state = self.queue.get()
    return self.state

  def delete( self ):
    self.loader.delete()

if __name__ == "__main__":
  print Loader.states
  print Loader.badStates
  print Loader.terminalStates
