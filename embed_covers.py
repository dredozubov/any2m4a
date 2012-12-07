import sys
import os
import subprocess
import shlex
import logging

from any2m4a import embed_cover_art


logging.basicConfig(filename='embed_cover.log', level=logging.INFO)


def run(paths):
    cdirs = []
    for path in paths:
        command = "find -s %s -name '*.m4a' -o -name '*.M4A'" % path
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        out, err = p.communicate()

        temp = out.split('\n')
        cdirs += temp

    cdirs = set([os.path.dirname(x) for x in cdirs[:-1]])
    total = len(cdirs)
    print cdirs

    for num, cdir in enumerate(cdirs, 1):
        print 'processing: %d of %d' % (num, total)

        embed_cover_art(cdir)


paths = sys.argv[1:] or '.'
run(paths)
