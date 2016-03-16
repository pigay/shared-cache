import os
import time
import datetime
import json

import lockfile
import loaders

def _validPid( pid ):
  return os.path.isdir( "/proc/%d" % pid )

class RepoFile( object ):
  __repodict_default = {"state" : loaders.Loader.states.UNKNOWN, "readers" : [], "writer" : None}

  def __init__( self, fn, lifetime = 15 ):
    self.fn = fn
    self.lock_fn = self.fn + ".lock"
    self.lock = lockfile.Lock( self.lock_fn, datetime.timedelta( seconds = lifetime ) )
    self.repodict = self.__repodict_default.copy()

  def __getitem__( self, key ):
    return self.repodict[key]

  def __setitem__( self, key, value ):
    self.repodict[key] = value

  def open( self ):
    self.lock.lock()

    if os.path.isfile( self.fn ):
      self.repodict.update( json.load( open( self.fn, 'r' ) ) )

  def close( self ):
    f = open( self.fn, "w" )
    json.dump( self.repodict, f )
    f.close()

    self.lock.unlock()

  def destroy( self ):
    os.unlink( self.fn )
    self.lock.unlock()

  def refresh( self ):
    self.lock.refresh()

class Repo( object ):
  def __init__( self, repoFile, loader_, pid = None ):
    self.repoFile = RepoFile( repoFile )
    self.loaderProcess = loaders.LoaderProcess( loader_ )
    self.pid = pid or os.getpid()

  def use( self ):
    def loadingState( repoFile ):
      return ( repoFile["state"] == loaders.Loader.states.IN_PROGRESS or
               repoFile["writer"] != None )

    # acquire write lock on repoFile
    self.repoFile.open()

    while loadingState( self.repoFile ):
      # repoFile is wtuck in loading state, try to fix bad state

      if not _validPid( self.repoFile["writer"] ):
        # writer gone, declare broken
        self.repoFile["writer"] = None
        self.repoFile["state"] = loaders.Loader.states.BROKEN

      if self.pid not in self.repoFile["readers"]:
        # register for reading
        self.repoFile["readers"].append( self.pid )

      # release reopFile
      self.repoFile.close()
      # wait 1 second before rechecking
      time.sleep( 1 )
      # load a possibly new state
      self.repoFile.open()

    if self.repoFile["state"] == loaders.Loader.states.OK:
      # repoFile is ok, ensure we are registered as reader
      if self.pid not in self.repoFile["readers"]:
        # register for reading
        self.repoFile["readers"].append( self.pid )
        print self.pid, "use registered in repo %s" % self.repoFile.fn
      else:
        print self.pid, "use already present in repo %s" % self.repoFile.fn

      self.repoFile.close()
      return True

    if self.repoFile["state"] in loaders.Loader.badStates:
      # repoFile is not in a correct state
      if self.repoFile["writer"] == None or not _validPid( self.repoFile["writer"] ):
        # no writer registered, or writer pid dead
        # register as a writer
        self.repoFile["writer"] = self.pid
        # launch loader in the background
        self.loaderProcess.start()
        self.repoFile["state"] = self.loaderProcess.getState()
        # save and release repoFile
        self.repoFile.close()
        print self.pid, "loading"
        done = False

        # wait for loader to finish
        while not done:
          time.sleep( 1 )
          state = self.loaderProcess.getState()
          self.repoFile.open()
          self.repoFile["state"] = state
          self.repoFile.close()
          done = state in loaders.Loader.terminalStates

        # release writer lock
        self.repoFile.open()
        self.repoFile["writer"] = None
        if state == loaders.Loader.states.OK and self.pid not in self.repoFile["readers"]:
            # register for reading
            self.repoFile["readers"].append( self.pid )
        self.repoFile.close()
        self.loaderProcess.join()
        return state == loaders.Loader.states.OK

    self.repoFile.close()
    print self.pid, 'uh? should not happen in Repo.use()', self.repoFile["state"]
    return False

  def unuse( self, rmdir ):
    self.repoFile.open()

    if self.pid in self.repoFile["readers"]:
      self.repoFile["readers"].remove( self.pid )

      # check for dead readers
      print self.pid, "other readers", self.repoFile["readers"]
      for otherpid in self.repoFile["readers"]:
        if not _validPid( otherpid ):
          self.repoFile["readers"].remove( otherpid )

      if len( self.repoFile["readers"] ) == 0:
        # we are the last reader, so destroy content and clean repoFile
        self.loaderProcess.delete()
        self.repoFile.destroy()
        if rmdir:
          os.rmdir( os.path.dirname( self.repoFile.fn ) )
        print self.pid, "destroy"
        return True

      self.repoFile.close()
      return True
    print self.pid, 'uh? should not happen in Repo.unuse()', self.repoFile["state"]
    return False
