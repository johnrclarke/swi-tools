#!/usr/bin/env python3.7
import sys
import re
import subprocess
from base64 import b64encode

# Just a simple implementation of a signing service for testing purposes.
# This signing service does not contact any signing server, it just uses a local 
# signing key and uses that to sign the given sha256. Eos signatures are over the
# sha256sum of the image with a 4k key size, we just handle that case.
# The swi-signature script does the sha256 on the image and passes it to this script
# (if the given options don't provide a signer's key, otherwise no need to call this
# script). The swi-signature also passes the filename were the resulting signature
# should be placed in.
# This script assumes the signer's key to be in /etc/swi-signing-devCA/signing.key
# (and does not bother to verify if it exists, this is just test code).

def main():

   if len( sys.argv ) != 3:
      print( "Error" )
      print( "usage: %s <sha256-string> <file-to-hold-signed-sha256-string>" % sys.argv[0] )
      sys.exit( -1 )

   digest = sys.argv[1]
   resultFile = sys.argv[2]
   keyFile = '/etc/swi-signing-devCA/signing.key'

   padSha256k4096="0001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00"
   sha256Magic = "3031300d060960864801650304020105000420"

   # Generate signature from sha256 hash and private key
   # pad the hash to the key length, and encode the hashing method into it as per RSAES-PKCS1-V1_5
   # find the modulo and exponent from the private key
   # compute the signature using modulo and exponent
   # convert it to base64 encoding

   digest = int( "%s%s%s" % ( padSha256k4096, sha256Magic, digest ), 16 )
   output = subprocess.check_output( [ 'openssl', 'rsa', '-in', keyFile,
                                      '-text', '-noout']).decode()
   m = int( re.sub( r'[ :\n]', '',
                    re.search( r'modulus:.*\n((?: +.*\n)+)',
                               output ).group ( 1 ) ),
            16 )
   e = int( re.sub( r'[ :\n]', '',
                    re.search( r'privateExponent:.*\n((?: +.*\n)+)',
                               output ).group ( 1 ) ),
            16 )
   signature = pow( digest, e, m )
   signature_bytes = signature.to_bytes( 512, byteorder='big', signed=False )
   b64_signature = b64encode( signature_bytes )
   with open( resultFile, 'wb+') as file:
      file.write( b64_signature )

   # For comparison, double check with openssl: Generate the signature from the file to sign and the private key
   # openssl dgst -sha256 -sign /etc/swi-signing-devCA/signing.key -out /tmp/digest /the/file/to/sign;
   # hexdump /tmp/digest | head -n 2
   # hexdump /tmp/digest | tail -n 2

if __name__ == '__main__':
   main()
