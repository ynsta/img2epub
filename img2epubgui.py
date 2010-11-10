#!/bin/env python
# -*- coding: utf8 -*-

import os
import sys

from PySide import QtCore, QtGui

from i2e import options, config, gui

def img2epubgui(opts, args):

    app = QtGui.QApplication(sys.argv)
    diag = gui.Img2Epub(opts = opts, args = args)
    diag.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    parser = options.genparser(config.VERSION, config.AUTHOR, config.AUTHOR_EMAIL, config.URL)
    (o, a) = parser.parse_args()
    img2epubgui(o, a)
