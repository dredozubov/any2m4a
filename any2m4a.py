import sys
import subprocess
import os
import shlex
import glob
import logging
import re

from itertools import chain

logging.basicConfig(filename='any2m4a_error.log', level=logging.INFO)


def shell_escape(s):
    return s.replace("'", "\'")


def convertwcue(filename, cuefile, cdir):
    args = tuple([shell_escape(d) for d in (cuefile, cdir, filename)])
    command = "xld -c '%s' -f alac -o '%s' '%s'" % args
    print 'executing: %s' % command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in p.stdout:
        print line.replace('\n', '')
    rc = p.poll()
    print 'rc: ', rc
    return True if rc == 0 else False


def convertdirect(filename, cdir):
    filename, cdir = [shell_escape(d) for d in (filename, cdir)]


def embed_cover_art(cdir):
    options = ['folder.png', 'folder.jpg', 'Folder.jpg', 'Folder.png',
            'cover.png', 'cover.jpg',
            'front.png', 'front.jpg', 'Front.jpg', 'Front.png',
            'f.png', 'f.jpg', 'F.png', 'F.jpg',
            'f*.png', 'F*.png', 'f*.jpg', 'F*.png',
            '*.png', '*.jpg']
    globs = chain.from_iterable(
            (glob.glob('%s/%s' % (cdir, option)) for option in options)
            )

    try:
        gl = next(globs)
    except StopIteration:
        gl = None
    except re.error:
        gl = None
        logging.error('Cover art embedding failed for %s' % cdir)

    if gl:
        cover_filename = gl
        audio_files = glob.iglob('%s/*.m4a' % cdir)
        for audio_file in audio_files:
            command = "mp4art --add '%s' '%s'" % (cover_filename, audio_file)
            print 'embedding cover art: %s' % command
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            for line in p.stdout:
                print line.replace('\n', '')
        return True
    else:
        return False


def lossless2alaccue(paths, delete_processed=False):
    cue_files = []
    for path in paths:
        command = "find -s %s -name '*.cue' -o -name '*.CUE'" % path
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        out, err = p.communicate()

        temp = out.split('\n')
        cue_files += temp

    # last splitted part is trash
    cue_dirs = [os.path.dirname(p) for p in cue_files[:-1]]

    cues = zip(cue_files, cue_dirs)
    print 'cues: ', cues

    total = len(cues)

    for num, (cfile, cdir) in enumerate(cues, 1):
        print 'processing: %d of %d' % (num, total)

        if not cfile:
            logging.info('skipping broken cue file in dir %s' % cdir)
            continue

        with open(cfile, 'r') as fd:
            files = [x for x in fd.readlines()
                    if x.startswith('FILE') or x.startswith('file')]
            filenames = [' '.join(s.split(' ')[1:-1]).strip('"')
                    for s in files if
                    [s.endswith(x) for x in ('flac', 'ape', 'wv')]]
            for filename in filenames:
                absfilename = '%s/%s' % (cdir, filename)
                successful = convertwcue(absfilename, cfile, cdir)

                print 'successful: ', successful

                if successful:
                    embed_cover_art(cdir)
                    if delete_processed:
                        print 'removing unused file: %s/%s' % (cdir, filename)
                        os.remove('%s/%s' % (cdir, filename))
                else:
                    logging.error(
                    '%s - xld completed with errors, processed file still in place: \n%s'  # noqa
                    % (absfilename, cfile))

                print
                break
    print 'complete!'


if __name__ == "__main__":
    paths = sys.argv[1:] or '.'

    lossless2alaccue(paths, delete_processed=False)
