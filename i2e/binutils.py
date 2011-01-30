#!/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess

execbin_cache = {}

def _lookup(names):
    pathlist = os.environ['PATH'].split(os.pathsep)
    for z in names:
        for p in pathlist:
            if os.path.isfile(os.path.join(p, z)):
                return os.path.join(p, z)
    return None

def find(bin):
    """
    Search the programs or the list of programs in the path environ
    return the value and store it in a cache table
    """
    if type(bin) == str:
        bin = [ bin ]
    if os.name == 'nt':
        bin = [ x + '.exe' for x in bin ]
    path = execbin_cache.get(bin[0], None)
    if not path:
        path = _lookup(bin)
        if path and os.access(path, os.X_OK):
            execbin_cache[bin[0]] = path
        else:
            path = None
    return path

def run(bin, args):
    if type(bin) == str:
        bin = [ bin ]

    if os.name == 'nt':
        bin  = [x.decode('iso-8859-1').encode('iso-8859-1') for x in bin]
        args = [x.decode('iso-8859-1').encode('iso-8859-1') for x in args]

    path = find(bin)
    if not path:
        return (1, None, None)
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        try:
            startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        except:
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        startupinfo = None
    p = subprocess.Popen([path] + args,
                         startupinfo=startupinfo,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True,
                         shell=False)

    (stdin, stderr) = p.communicate()
    return (p.returncode, stdin, stderr)
