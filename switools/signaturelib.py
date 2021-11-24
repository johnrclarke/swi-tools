# Copyright (c) 2018 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.

from __future__ import absolute_import, division, print_function
import os
import subprocess

SWI_SIG_FILE_NAME = 'swi-signature'
SWIX_SIG_FILE_NAME = 'swix-signature'

def getSigFileName( swiFile ):
   if swiFile.lower().endswith( ".swix" ):
      return SWIX_SIG_FILE_NAME
   return SWI_SIG_FILE_NAME

def runCmd( cmd, workDir ):
   try:
      subprocess.check_call( cmd.split(" "), cwd=workDir )
   except subprocess.CalledProcessError:
      return False
   return True

def getOptimizations( swi, workDir ):
   # unzip spits warnings when extracting non-existant files, so check first :-(
   cmd = "unzip -Z1 %s" % swi
   if not "swimSqshMap" in str( subprocess.check_output( cmd.split(" ") ) ):
      return None # legacy image
   cmd = "unzip -qq -o %s swimSqshMap" % os.path.abspath( swi )
   try:
      subprocess.check_call( cmd.split(" "), cwd=workDir )
   except subprocess.CalledProcessError:
      return None # legacy image

   optims = []
   with open( "%s/swimSqshMap" % workDir ) as f:
      for line in f:
         optim, _ = line.split( "=", 1 )
         optims.append( optim )
   return optims

def extractSwadapt( swi, workDir ):
   cmd = "unzip -o -qq %s swadapt" % os.path.abspath( swi )
   return runCmd( cmd, workDir )

def checkIsSwiFile( swi, workDir ):
   if not os.path.isfile( swi ):
      return False
   # unzip spits warnings when extracting non-existant files, so check first :-(
   cmd = "unzip -Z1 %s" % swi
   if not "version" in subprocess.check_output( cmd.split(" ") ).decode( 'utf-8' ).split():
      return None # legacy image
   cmd = "unzip -o -qq %s version" % os.path.abspath( swi )
   return runCmd( cmd, workDir )

def adaptSwi( swi, optimImage, optim, workDir ):
   cmd = "%s/swadapt %s %s %s" % ( workDir, os.path.abspath( swi ), optimImage, optim )
   return runCmd( cmd, workDir )
