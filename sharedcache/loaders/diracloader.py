import loader

import os
import time

import DIRAC

__all__ = ['DiracLoader']

# The following two lines are required for the DIRAC loading to work
from DIRAC.Core.Base import Script
Script.enableCS()

from DIRAC.Interfaces.API.Dirac import Dirac
_dirac = Dirac()

class DiracLoader( loader.Loader ):
  def __init__( self, lfn, destinationDir = None ):
    self.lfn = lfn
    self.destinationDir = destinationDir or os.getcwd()
    self.destination = os.path.join( self.destinationDir, os.path.basename( self.lfn ) )

  def __call__( self, queue ):
    queue.put( loader.Loader.states.IN_PROGRESS )

    ret = _dirac.getFile( self.lfn, self.destinationDir )

    if not ret['OK']:
      queue.put( loader.Loader.states.BROKEN )
      print ret['Message']
      return

    queue.put( loader.Loader.states.OK )


  def delete( self ):
    os.unlink( self.destination )

  def pathList( self ):
    return [self.destination]
