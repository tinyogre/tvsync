#!/usr/bin/env python

import os, sys, shutil
import ConfigParser

os.system('mkdir -p ' + os.path.expanduser('~/.tvsync.d'))
c = ConfigParser.ConfigParser()
c.read(os.path.expanduser('~/.tvsync.d/dispatch'))

# dispatch_file will:
# 1) Make a copy of the input in a temp location (dispatch.temppath)
# 2) Move the copy to the archive path (dispatch.archive)
# 3) Move the original to either dispatch.HD or dispatch.SD depending only on extension
# Note this means the original will be gone.  Both operations are done as moves rather than copies
# so that whatever else is watching those directories sees only the complete file appear

# Using os.system rather than shutil fns because shutil.move was
# causing me issues on the Mac where I use this.  I don't know why
# it's not the same as system('mv') but it's not.
def dispatch_file(infile):
    path, file = os.path.split(infile)
    base,ext = os.path.splitext(file)

    temploc = os.path.expanduser(c.get('dispatch', 'temppath'))
    print "Copy " + infile + " => " + temploc
    shutil.copyfile(infile, temploc)
    cmd = 'mv "' + temploc + '" "'+ os.path.expanduser(c.get('dispatch', 'archive'))
    print cmd
    os.system(cmd)

    
    if ext == '.mkv':
        dest = os.path.expanduser(c.get('dispatch', 'HD'))
    else:
        dest = os.path.expanduser(c.get('dispatch', 'SD'))

    if len(dest) > 0
    cmd = 'mv "' + infile + '" "' + dest + '"'
    print cmd
    os.system(cmd)
