# -*- coding: utf8 -*-

import re
import os
import unicodedata

amap = { 'a' : ['à','á','â','ã','ä'],
         'c' : ['ç'],
         'e' : ['è','é','ê','ë'],
         'i' : ['ì','í','î','ï'],
         'n' : ['ñ'],
         'o' : ['ò','ó','ô','õ','ö'],
         'u' : ['ù','ú','û','ü'],
         'y' : ['ý','ÿ'],
         'A' : ['À','Á','Â','Ã','Ä'],
         'C' : ['Ç'],
         'E' : ['È','É','Ê','Ë'],
         'I' : ['Ì','Í','Î','Ï'],
         'N' : ['Ñ'],
         'O' : ['Ò','Ó','Ô','Õ','Ö'],
         'U' : ['Ù','Ú','Û','Ü'],
         'Y' : ['Ý'] }

def remove_accent(string):
    for (c, la) in amap.iteritems():
        for i in la:
            string = string.replace(i, c)
    return string

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
