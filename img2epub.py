#!/bin/env python
# -*- coding: utf8 -*-

import re
import os
import sys
import shutil
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import options
import textutils
import binutils
import fileutils
import epub

from config import *

def img2epub(opts, arg):

    # Test dependencies:
    if not binutils.find(['7z', '7za']):
        print "7z not found in PATH, Exiting"
        sys.exit(1)
    if not binutils.find(['convert']):
        print "convert not found in PATH, Exiting"
        sys.exit(1)
    if not binutils.find(['identify']):
        print "identify not found in PATH, Exiting"
        sys.exit(1)

    # Generate output with extension
    epub_name = '_'.join([opts.creator, opts.title, opts.language])
    epub_name = ''.join([ c for c in re.split('[^a-zA-Z0-9,_ -]', epub_name) ])
    epub_name = textutils.remove_accent(epub_name.lower())

    if opts.output:
        if os.path.isdir(opts.output):
            opts.output = os.path.join(opts.output, epub_name)
    else:
        opts.output = epub_name
    opts.output = fileutils.add_ext(opts.output, '.epub')

    # Check and parse input
    if len(arg) == 0:
        print "No input, Exiting (--help form more informations)"
        sys.exit(1)
    def exists(f):
        if not os.path.exists(f):
            print "Input '%s' not found" % f
            return False
        else:
            return True
    if not reduce(lambda x, y: x and y, [exists(t) for t in arg]):
        print "Exiting"
        sys.exit(1)

    # Temporary directory
    tmpd = tempfile.mkdtemp()

    # Extracting archives given as program arguments
    alist = fileutils.find_by_exts(arg, ARCHEXTS)
    for a in alist:
        adir = os.path.join(tmpd, fileutils.rem_ext(a))
        (r,s,e) = binutils.run('7z', ['x', a, '-o' + adir])
        if not r:
            arg.append(adir)

    # Looking for images
    flist = fileutils.find_by_exts(arg, IMGEXTS)
    image_list   = [os.path.abspath(x) for x in flist]
    chapter_map  = {}
    chapter_list = []
    for i in range(len(flist)):
        cname = os.path.basename(os.path.dirname(flist[i]))
        cname = textutils.sentencify(cname)
        if not chapter_map.get(cname):
            chapter_map[cname] = [i]
            chapter_list.append(cname)
        else:
            chapter_map[cname].append(i)

    # Epub creation
    epub.create_epub(opts, opts.output, image_list, chapter_list, chapter_map)

    # Temporary directory removed
    shutil.rmtree(tmpd, ignore_errors=True)


if __name__ == '__main__':
    parser = options.genparser(VERSION, AUTHOR, URL)
    (o, a) = parser.parse_args()
    img2epub(o, a)
