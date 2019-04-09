# USAGE: python writetofile.py /path/to/file text

import sys

with open(sys.argv[1], 'w') as theFile: # Load file
    theFile.write(sys.argv[2])
