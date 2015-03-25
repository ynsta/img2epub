# -*- coding: utf8 -*-

import re
import os
import unicodedata

def remove_accent(string):
    return unicodedata.normalize('NFKD', string)

reg_specials = re.compile(u"[^0-9a-z ._'-]", re.I | re.U)
reg_mulspaces = re.compile('\s+')

def filify(string):
    string = remove_accent(string)
    string = unicode(string, errors = 'ignore')
    string = reg_specials.sub('', string)
    string = reg_mulspaces.sub(' ', string)
    return string.strip()

reg_num      = re.compile('([0-9]+)')
reg_num_path = re.compile('([/:\\\]|[0-9]+)')

def humansort(stringlist):
    def cut(string):
        def retype(string):
            try:
                return int(string)
            except:
                return string.lower()
        return [ retype(elt) for elt in reg_num_path.split(string) ]
    stringlist.sort(key = cut)

def sentencify(string):
    def cut(string):
        def retype(string):
            try:
                return str(int(string))
            except:
                return string.lower()
        return [ retype(elt) for elt in reg_num.split(string) ]
    string = ' '.join(cut(string))
    string = re.sub('[ _-]+', ' ', string)
    return string.strip().capitalize()
