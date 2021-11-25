# Copyright (c) 2018 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.

from __future__ import absolute_import, division, print_function

import os

SWI_SIG_FILE_NAME = 'swi-signature'
SWIX_SIG_FILE_NAME = 'swix-signature'

def getSigFileName( swiFile ):
   if swiFile.lower().endswith( ".swix" ):
      return SWIX_SIG_FILE_NAME
   return SWI_SIG_FILE_NAME

def getOptimizations( swi ):
   optims = []
   if 'swimSqshMap' in swi.namelist():
       for line in swi.read( 'swimSqshMap' ).splitlines():
         optim, _ = line.decode().split( "=", 1 )
         optims.append( optim )
   return optims

def extractSwadapt( swi, workDir ):
   if 'swadapt' not in swi.namelist():
       return False
   swi.extract( 'swadapt', workDir )
   os.chmod( '{}/swadapt'.format( workDir ), 0o755 )
   return True
