import sys
import subprocess
import os
import shlex


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


def lossless2alaccue(paths, delete_processed=False):
    cue_files = []
    for path in paths:
        command = 'find -s %s -regex .*\\.cue$' % path
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        out, err = p.communicate()

        temp = out.split('\n')
        cue_files += temp

    # last splitted part is trash
    cue_dirs = [os.path.dirname(p) for p in cue_files[:-1]]

    cues = zip(cue_files, cue_dirs)

    total = len(cues)

    for num, (cfile, cdir) in enumerate(cues, 1):
        print 'processing: %d of %d' % (num, total)
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
                if successful and delete_processed:
                    print 'removing unused file: %s' % filename
                    os.remove(filename)
                print
                break
    print 'complete!'

paths = sys.argv[1:] or '.'

lossless2alaccue(paths, delete_processed=False)
