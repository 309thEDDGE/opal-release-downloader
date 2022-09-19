import sys
import os

from .list import main as list_main
from .fetch import main as fetch_main
from .verify import main as verify_main
from .download import main as dl_main


def main():
    this_dir = os.path.dirname(__file__)

    if len(sys.argv) <= 1:
        sys.argv = [ os.path.join(this_dir, 'download.py') ]
        dl_main()
        return


    cmdstr = sys.argv[1].lower()
    subcmds = {
            'list': {'filename': 'list.py', 'main': list_main},
            'fetch': {'filename': 'fetch.py', 'main': fetch_main},
            'verify': {'filename': 'verify.py', 'main':verify_main},
            }

    if cmdstr in subcmds:
        cmd = subcmds[cmdstr]
        fname = os.path.join(this_dir, cmd['filename'])
        sys.argv = [fname, *sys.argv[2:]]
        cmd['main']()

    else:
        fname = os.path.join(this_dir, 'download.py')
        sys.argv = [fname, *sys.argv[1:]]
        dl_main()


if __name__ == '__main__':
    main()
