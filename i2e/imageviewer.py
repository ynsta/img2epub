from PySide import QtCore, QtGui

import os
import shutil
import tempfile
import epub

class ImageViewer(QtGui.QWidget):

    def __init__(self, opts):
        super(ImageViewer, self).__init__()
        self.printer = QtGui.QPrinter()

        self.opts = opts

        self.imageLabel0 = QtGui.QLabel()
        self.imageLabel0.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel0.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                       QtGui.QSizePolicy.Ignored)
        self.imageLabel0.setScaledContents(True)
        self.imageLabel1 = QtGui.QLabel()
        self.imageLabel1.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel1.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                       QtGui.QSizePolicy.Ignored)
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.imageLabel0, 0, 0)
        mainLayout.addWidget(self.imageLabel1, 0, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Img2Epub Viewer")
        self.resize(self.opts.hsize*2, self.opts.vsize)

        self.tmpd = tempfile.mkdtemp(prefix='img2epub_iv_')

    def __del__(self):
        shutil.rmtree(self.tmpd, ignore_errors=True)

    def setImage(self, imageName):

        names = [ imageName ] + epub.img_convert(self.opts, imageName, os.path.join(self.tmpd, 'preview-'), 0)

        images = [ QtGui.QImage(x) for x in names ]

        self.resize(images[1].width()*2, images[1].height())

        self.imageLabel0.setPixmap(QtGui.QPixmap.fromImage(images[0]))
        self.imageLabel1.setPixmap(QtGui.QPixmap.fromImage(images[1]))

