#!/bin/env python
# -*- coding: utf8 -*-

import os
import sys

def create(start_path):

    python_path = sys.prefix
    pyw_path    = os.path.abspath(os.path.join(python_path, 'pythonw.exe'))
    script_file = os.path.join(os.path.join(python_path, 'Scripts', 'img2epubgui.py'))
    programs_path = os.path.join(start_path, 'Img2epub')

    try:
        os.mkdir(programs_path)
    except:
        None
    directory_created(programs_path)

    lnk_file = os.path.join(programs_path, 'Img2Epub.lnk')

    create_shortcut(pyw_path,
                    'Image to Epub converter',
                    lnk_file,
                    script_file,
                    '%HOMEDRIVE%' + os.sep + '%HOMEPATH%')
    file_created(lnk_file)


if sys.argv[1] == '-install':
    try:
        create(get_special_folder_path('CSIDL_COMMON_PROGRAMS'))
    except OSError:
        create(get_special_folder_path('CSIDL_PROGRAMS'))
