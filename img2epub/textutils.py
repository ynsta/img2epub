# -*- coding: utf8 -*-

import re
import os

amap = { 'a' : re.compile('[àáâãä]'),
         'c' : re.compile('[ç]'),
         'e' : re.compile('[èéêë]'),
         'i' : re.compile('[ìíîï]'),
         'n' : re.compile('[ñ]'),
         'o' : re.compile('[òóôõö]'),
         'u' : re.compile('[ùúûü]'),
         'y' : re.compile('[ýÿ]'),
         'A' : re.compile('[ÀÁÂÃÄ]'),
         'C' : re.compile('[Ç]'),
         'E' : re.compile('[ÈÉÊË]'),
         'I' : re.compile('[ÌÍÎÏ]'),
         'N' : re.compile('[Ñ]'),
         'O' : re.compile('[ÒÓÔÕÖ]'),
         'U' : re.compile('[ÙÚÛÜ]'),
         'Y' : re.compile('[Ý]')}

def remove_accent(string):
    for (c, reg) in amap.iteritems():
        string = reg.sub(c, string)
    return string

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
