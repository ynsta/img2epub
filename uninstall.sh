#!/bin/bash

PREFIX=/usr/local

if [ ! -f install.sh ] || [ ! -f img2epub.in ]; then
    echo 1>&2 "uninstall.sh must be launch from the install directory"
    exit 1
fi

IFS='
'
rm -f $(find . -name '*~')
unset IFS

rm -rvf ${PREFIX}/share/img2epub
rm -vf  ${PREFIX}/bin/img2epub
