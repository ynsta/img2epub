import sys
import uuid
import re
import os
import sys
import shutil
import tempfile

from PySide import QtCore, QtGui

from ui_img2epub import Ui_DialogImg2Epub

import config
import binutils
import options
import textutils
import binutils
import fileutils
import epub

def criticalMessage(parent, msg):
    QtGui.QMessageBox.critical(parent, 'Img2Epub Critical Error', msg)

def warnMessage(parent, msg):
    QtGui.QMessageBox.warning(parent, 'Img2Epub Error', msg)

class OutLog(QtCore.QObject):
    def __init__(self, color=QtCore.Qt.black, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.color = color
    def write(self, msg):
        self.emit(QtCore.SIGNAL("logPosted(const QString &, const QColor &)"), msg, self.color)


class EpubThreadConvert(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def setParams(self, opts, output, image_list, chapter_list, chapter_map):
        self.opts         = opts
        self.output       = output
        self.image_list   = image_list
        self.chapter_list = chapter_list
        self.chapter_map  = chapter_map
        self.progress     = 0

    def setProgress(self):
        self.progress = self.progress + 1
        self.emit(QtCore.SIGNAL("progressValueChanged(int)"), self.progress)

    def run(self):
        self.progress = 0
        epub.create_epub(self.opts,
                         self.output,
                         self.image_list,
                         self.chapter_list,
                         self.chapter_map,
                         self.setProgress)

class EpubThreadExtract(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def setParams(self, archive_list, out_dir):
        self.archive_list = archive_list
        self.out_dir      = out_dir
        self.progress     = 0
        self.outputs      = []

    def getOutput(self):
        return self.outputs

    def setProgress(self):
        self.progress = self.progress + 1
        self.emit(QtCore.SIGNAL("progressValueChanged(int)"), self.progress)

    def run(self):
        self.progress = 0
        self.outputs  = []
        for a in self.archive_list:
            print 'Extracting', a,
            adir = os.path.join(self.out_dir, fileutils.rem_ext(os.path.basename(a)))
            (r,s,e) = binutils.run('7z', ['x', a, '-y', '-o' + adir])
            print 'Done'
            self.setProgress()
            if not r:
                self.outputs.append(adir)


class Img2Epub(QtGui.QWidget):
    def __init__(self, parent=None, opts=None, args=None):
        QtGui.QWidget.__init__(self, parent)

        error = False

        self.ui = Ui_DialogImg2Epub()
        self.ui.setupUi(self)

        sys.stdout = OutLog()
        sys.stderr = OutLog(QtCore.Qt.red)

        self.connect(sys.stdout,
                     QtCore.SIGNAL("logPosted(const QString &, const QColor &)"),
                     self.writeLog)
        self.connect(sys.stderr,
                     QtCore.SIGNAL("logPosted(const QString &, const QColor &)"),
                     self.writeLog)

        # Test dependencies:
        if not binutils.find(['7z', '7za']):
            criticalMessage(self, '7z not found in PATH !<br/><br/>'
                            '<br/>'
                            'Please add 7-Zip to your PATH.')
            error = True
        if not binutils.find(['convert']):
            criticalMessage(self, 'convert not found in PATH !<br/><br/>'
                            'Please add ImageMagick to your PATH.')
            error = True
        if not binutils.find(['identify']):
            criticalMessage(self, 'identify not found in PATH !<br/><br/>'
                            'Please add ImageMagick to your PATH.')
            error = True

        if error:
            sys.exit(1)

        self.epubThreadConvert = EpubThreadConvert()
        self.connect(self.epubThreadConvert,
                     QtCore.SIGNAL("progressValueChanged(int)"),
                     self.setProgress)
        self.connect(self.epubThreadConvert,
                     QtCore.SIGNAL("finished()"),
                     self.epubThreadConvertFinished)

        self.epubThreadExtract = EpubThreadExtract()
        self.connect(self.epubThreadExtract,
                     QtCore.SIGNAL("progressValueChanged(int)"),
                     self.setProgress)
        self.connect(self.epubThreadExtract,
                     QtCore.SIGNAL("finished()"),
                     self.epubThreadExtractFinished)

        self.tmpd = tempfile.mkdtemp()

        self.inputs = None

        self.opts = opts

        self.ui.lineEditTitle.setText(opts.title)
        self.ui.lineEditCreator.setText(opts.creator)
        self.ui.lineEditLanguage.setText(opts.language)
        self.ui.lineEditPublisher.setText(opts.publisher)
        self.ui.lineEditDate.setText(opts.date)
        self.ui.lineEditSubject.setText(opts.subject)
        self.ui.lineEditType.setText(opts.type)
        self.ui.lineEditUUID.setText(opts.uuid)

        self.ui.spinBoxWidth.setValue(opts.hsize)
        self.ui.spinBoxHeight.setValue(opts.vsize)
        self.ui.spinBoxColors.setValue(opts.colors)

        self.ui.checkBoxDither.setChecked(opts.dither)

        if opts.cut == 'A':
            self.ui.radioButtonCutA.setChecked(True)
        elif opts.cut == 'H':
            self.ui.radioButtonCutH.setChecked(True)
        elif opts.cut == 'R':
            self.ui.radioButtonCutR.setChecked(True)
        elif opts.cut == 'V':
            self.ui.radioButtonCutV.setChecked(True)
        else:
            self.ui.radioButtonCut0.setChecked(True)

        self.ui.checkBoxTrim.setChecked(not opts.notrim)
        self.ui.spinBoxTrimValue.setValue(opts.trim_val)
        self.ui.spinBoxTrimIter.setValue(opts.trim_iter)

        epub_name = '_'.join([opts.creator, opts.title, opts.language])
        epub_name = ''.join([ c for c in re.split('[^a-zA-Z0-9,_ -]', epub_name) ])
        epub_name = textutils.remove_accent(epub_name.lower())

        if opts.output:
            opts.output = opts.output.replace('/', os.sep)
            if os.path.isdir(opts.output):
                opts.output = os.path.join(opts.output, epub_name)
        else:
            opts.output = epub_name
        opts.output = fileutils.add_ext(opts.output, '.epub')

        if opts.output:
            self.ui.lineEditOutput.setText(opts.output)

        if args and len(args):
            self.ui.lineEditInputs.setText('|'.join(args).replace('/', os.sep))
            self.inputsChanged()
        self.runEnable()


    def __del__(self):
        shutil.rmtree(self.tmpd, ignore_errors=True)


    def inputsChanged(self):
        txt = self.ui.lineEditInputs.text().strip()

        inputs = txt.split('|')

        if txt == '' or len(inputs) == 0 or self.inputs == inputs:
            return

        self.disabled_widgets = [self.ui.lineEditOutput,
                                 self.ui.lineEditInputs,
                                 self.ui.toolButtonOutput,
                                 self.ui.toolButtonInputs,
                                 self.ui.toolButtonInputDir,
                                 self.ui.pushButtonRun]
        for w in self.disabled_widgets:
            w.setEnabled(False)

        self.inputs = inputs

        notfound = ""
        for i in inputs:
            if not os.path.exists(i):
                notfound = notfound + ('"' + i + '" not found<br/>')

        if notfound != "":
            warnMessage(self, notfound)
            return

        alist = fileutils.find_by_exts(inputs, config.ARCHEXTS)
        self.ui.progressBar.setRange(0, len(alist))
        self.epubThreadExtract.setParams(alist, self.tmpd)
        self.epubThreadExtract.start()


    def runEnable(self):
        try:
            otext = self.ui.lineEditOutput.text()
            opath = os.path.dirname(os.path.abspath(otext))
            res = (len(self.image_list) > 0 and
                   os.access(opath, os.W_OK))
        except:
            res = False

        self.ui.pushButtonRun.setEnabled(res)


    @QtCore.Slot()
    def on_lineEditInputs_editingFinished(self):
        self.inputsChanged()
        self.runEnable()

    @QtCore.Slot()
    def on_lineEditOutput_editingFinished(self):
        self.runEnable()

    @QtCore.Slot()
    def on_pushButtonUUID_released(self):
        self.ui.lineEditUUID.setText(str(uuid.uuid1()))


    @QtCore.Slot()
    def on_toolButtonInputs_released(self):

        img_filter  = 'Images ('    + ' '.join(['*.' + i for i in config.IMGEXTS]) + ')'
        arch_filter = 'Archives (' + ' '.join(['*.' + i for i in config.ARCHEXTS]) + ')'

        lst = QtGui.QFileDialog.getOpenFileNames(self,
                                                 "Select one or more files to open",
                                                 ".",
                                                 img_filter + ';;' + arch_filter)
        if lst and lst[0]:
            self.ui.lineEditInputs.setText('|'.join(lst[0]))

        self.inputsChanged()
        self.runEnable()

    @QtCore.Slot()
    def on_toolButtonInputDir_released(self):
        f = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images")
        if f:
            self.ui.lineEditInputs.setText(f.replace('/', os.sep))
        self.inputsChanged()
        self.runEnable()

    @QtCore.Slot()
    def on_toolButtonOutput_released(self):
        f = QtGui.QFileDialog.getSaveFileName(self, "Ouput epub file",
                                              ".",  "epub (*.epub)")
        if f:
            self.ui.lineEditOutput.setText(f[0].replace('/', os.sep))

        self.runEnable()


    @QtCore.Slot()
    def on_pushButtonRun_released(self):
        self.disabled_widgets = [self.ui.tabEpub,
                                 self.ui.lineEditOutput,
                                 self.ui.lineEditInputs,
                                 self.ui.toolButtonOutput,
                                 self.ui.toolButtonInputs,
                                 self.ui.toolButtonInputDir,
                                 self.ui.tabImageSettings,
                                 self.ui.pushButtonRun]
        for w in self.disabled_widgets:
            w.setEnabled(False)
        self.ui.progressBar.setRange(0, len(self.image_list))
        self.epubThreadConvert.setParams(self.opts,
                                  self.ui.lineEditOutput.text(),
                                  self.image_list,
                                  self.chapter_list,
                                  self.chapter_map)
        self.epubThreadConvert.start()



    @QtCore.Slot()
    def on_lineEditTitle_editingFinished(self):
        self.opts.title = self.ui.lineEditTitle.text()

    @QtCore.Slot()
    def on_lineEditCreator_editingFinished(self):
        self.opts.creator = self.ui.lineEditCreator.text()

    @QtCore.Slot()
    def on_lineEditLanguage_editingFinished(self):
        self.opts.language = self.ui.lineEditLanguage.text()

    @QtCore.Slot()
    def on_lineEditPublisher_editingFinished(self):
        self.opts.publisher = self.ui.lineEditPublisher.text()

    @QtCore.Slot()
    def on_lineEditDate_editingFinished(self):
        self.opts.date = self.ui.lineEditDate.text()

    @QtCore.Slot()
    def on_lineEditSubject_editingFinished(self):
        self.opts.subject = self.ui.lineEditSubject.text()

    @QtCore.Slot()
    def on_lineEditType_editingFinished(self):
        self.opts.type = self.ui.lineEditType.text()

    @QtCore.Slot()
    def on_lineEditUUID_editingFinished(self):
        self.opts.uuid = self.ui.lineEditUUID.text()

    @QtCore.Slot()
    def on_spinBoxWidth_editingFinished(self):
        self.opts.hsize = self.ui.spinBoxWidth.value()

    @QtCore.Slot()
    def on_spinBoxHeight_editingFinished(self):
        self.opts.vsize = self.ui.spinBoxHeight.value()

    @QtCore.Slot()
    def on_spinBoxColors_editingFinished(self):
        self.opts.colors = self.ui.spinBoxColors.value()

    @QtCore.Slot()
    def on_spinBoxTrimValue_editingFinished(self):
        self.opts.trim_val = self.ui.spinBoxTrimValue.value()

    @QtCore.Slot()
    def on_spinBoxTrimIter_editingFinished(self):
        self.opts.trim_iter = self.ui.spinBoxTrimIter.value()

    @QtCore.Slot(bool)
    def on_checkBoxTrim_toggled(self, state):
        self.opts.notrim = not state

    @QtCore.Slot(bool)
    def on_checkBoxDither_toggled(self, state):
        self.opts.dither = state

    @QtCore.Slot(bool)
    def on_radioButtonCutA_toggled(self, state):
        if state:
            self.opts.cut = 'A'

    @QtCore.Slot(bool)
    def on_radioButtonCutH_toggled(self, state):
        if state:
            self.opts.cut = 'H'

    @QtCore.Slot(bool)
    def on_radioButtonCutR_toggled(self, state):
        if state:
            self.opts.cut = 'R'

    @QtCore.Slot(bool)
    def on_radioButtonCutV_toggled(self, state):
        if state:
            self.opts.cut = 'V'

    @QtCore.Slot(bool)
    def on_radioButtonCut0_toggled(self, state):
        if state:
            self.opts.cut = None

    def epubThreadConvertFinished(self):
        for w in self.disabled_widgets:
            w.setEnabled(True)
        self.ui.progressBar.reset()

    def epubThreadExtractFinished(self):

        for w in self.disabled_widgets:
            w.setEnabled(True)
        self.ui.progressBar.reset()

        inputs  = self.inputs
        zinputs = self.epubThreadExtract.getOutput()

        # Looking for images
        flist = fileutils.find_by_exts(inputs + zinputs, config.IMGEXTS)
        self.image_list   = [os.path.abspath(x) for x in flist]
        self.chapter_map  = {}
        self.chapter_list = []

        for i in range(len(flist)):
            cname = os.path.basename(os.path.dirname(flist[i]))
            cname = textutils.sentencify(cname)
            if not self.chapter_map.get(cname):
                self.chapter_map[cname] = [i]
                self.chapter_list.append(cname)
            else:
                self.chapter_map[cname].append(i)

        chapter_tv_list = [QtGui.QTreeWidgetItem([c,]) for c in self.chapter_list]
        for i in range(len(self.chapter_list)):
            img_tv_list = [QtGui.QTreeWidgetItem([(self.image_list[c]),]) \
                               for c in self.chapter_map[self.chapter_list[i]]]
            chapter_tv_list[i].addChildren(img_tv_list)


        while self.ui.treeWidgetFiles.takeTopLevelItem(0):
            None

        self.ui.treeWidgetFiles.addTopLevelItems(chapter_tv_list)


    def writeLog(self, msg, color):
        self.ui.textEditMessageLog.moveCursor(QtGui.QTextCursor.End)
        self.ui.textEditMessageLog.setTextColor(color)
        self.ui.textEditMessageLog.insertPlainText(msg)

    def setProgress(self, val):
        self.ui.progressBar.setValue(val)
