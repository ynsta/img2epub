#!/bin/env python
# -*- coding: utf8 -*-

import uuid
import datetime
import optparse

def genparser(version, author, email, url):
    NOW  = str(datetime.datetime.now().year)
    UUID = '00000000-0000-0000-0000-000000000000'

    parser = optparse.OptionParser(usage="%prog [options] input",
                                   version="%prog " + version + ' by ' + author + ' <' + email + '>\n' + url,
                                   description="Creates an epub book from a CBR, "
                                   "a CBZ or a directory with images. Last version is available at " + url)

    parser.add_option("-o", "--output", dest="output", metavar="OUTPUT", default=None,
                      help="the output filename")

    group = optparse.OptionGroup(parser, "EPUB properties options")

    group.add_option("-t", "--title", dest="title", metavar="TITLE", default="unknown",
                      help="the title of the book [default: %default]")

    group.add_option("-c", "--creator", dest="creator", metavar="CREATOR", default="Img2Epub",
                      help="the creator of the book [default: %default]")

    group.add_option("-l", "--language", dest="language", metavar="LANGUAGE", default="en",
                      help="the language of the book [default: %default]")

    group.add_option("-p", "--publisher", dest="publisher", metavar="PUBLISHER", default="Img2Epub",
                      help="the publisher  of the book [default: %default]")

    group.add_option("-d", "--date", dest="date", metavar="DATE", default=NOW,
                      help="the date of the book [default: %default]")

    group.add_option("-s", "--subject", dest="subject", metavar="SUBJECT", default="Images",
                      help="the subject of the book [default: %default]")

    group.add_option("-T", "--type", dest="type", metavar="TYPE", default="Manga, Comics",
                      help="the type of the book [default: %default]")

    group.add_option("-u", "--uuid", dest="uuid", metavar="UUID", default=UUID,
                      help="the Universal Unique Identifier of the book [default: %default]")

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Images output options")

    group.add_option("-V", "--vsize", dest="vsize", metavar="VSIZE", default=750, type="int",
                      help="the maximal vertical size of images in pixels [default: %default]")

    group.add_option("-H", "--hsize", dest="hsize", metavar="HSIZE", default=580, type="int",
                      help="the maximal horizontal size of images in pixels [default: %default]")

    group.add_option("-C", "--colors", dest="colors", metavar="COLORS", default=16, type="int",
                      help="2-256, the number of output greyscale colors [default: %default]")

    group.add_option("-D", "--dither", dest="dither", default=False, action="store_true",
                      help="activate dithering for color reduction [default: %default]")

    group.add_option("-U", "--cut", dest="cut", metavar="A|H|R|V", default=None,
                      help="A|H|R|V, A = cut all images in two,"
                      "H = cut only if image width > height,"
                      "R = cut only if image width > height and switch the 2 images,"
                      "V = cut only if image width < height [default: no cut]")

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Border trimming options")

    group.add_option("-n", "--notrim", dest="notrim", default=True, action="store_false",
                      help="disable broder trim")

    group.add_option("-v", "--trim_val", dest="trim_val", metavar="VAL", default=20,
                      help="0-100, the % of tolerance from corner pixels to trim [default: %default]")

    group.add_option("-i", "--trim_iter", dest="trim_iter", metavar="ITER", default=2,
                      help="the number of trim iterations [default: %default]")

    parser.add_option_group(group)

    return parser

