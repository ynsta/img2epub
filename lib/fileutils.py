#!/bin/env python
# -*- coding: utf8 -*-

import os
import textutils

def find_by_exts(dirs, exts):
    def isext(f):
        if not os.path.isfile(f):
            return False
        tmp = f.rsplit('.', 1)
        if len(tmp) != 2:
            return False
        ext = tmp[1].lower()
        return reduce(lambda x, y: x or y, [ x == ext for x in exts])

    def visit(lst, dirname, names):
        for n in names:
            path = os.path.join(dirname, n)
            if isext(path):
                lst.append(path)
    flist = []
    for d in dirs:
        tmp = []
        if os.path.isdir(d):
            os.path.walk(d, visit, tmp)
        elif isext(d):
            tmp = [ d ]
        textutils.humansort(tmp)
        flist = flist + tmp
    return flist


def rem_ext(name):
    return name.rsplit('.', 1)[0]

def add_ext(name, ext):
    if len(name) < len(ext) or name[-len(ext):].lower() != ext.lower():
        return name + ext
    else:
        return name
