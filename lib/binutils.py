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
    if type(bin) == str:
        bin = [ bin ]
    if os.name == 'nt':
        bin = [ x + '.exe' for x in bin ]
    path = execbin_cache.get(bin[0], None)
    if not path:
        path = _lookup(bin)
        if os.access(path, os.X_OK):
            execbin_cache[bin[0]] = path
        else:
            path = None
    return path

def run(bin, args):
    if type(bin) == str:
        bin = [ bin ]
    path = find(bin)
    if not path:
        return (1, None, None)
    p = subprocess.Popen([path] + args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
    (stdin, stderr) = p.communicate()
    return (p.returncode, stdin, stderr)
