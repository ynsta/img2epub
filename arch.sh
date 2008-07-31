#!/bin/bash

if [ ! -f install.sh ] || [ ! -f img2epub.in ]; then
    echo 1>&2 "install.sh must be launch from the install directory"
    exit 1
fi

VERSION=$(cat VERSION | tr 'A-Z' 'a-z')
cd ..

tar -cvzf img2epub-$VERSION.tar.gz img2epub

ARCHNAME=img2epub-${VERSION}_$(md5sum img2epub-$VERSION.tar.gz | awk '{ print $1 }').tar.gz
mv img2epub-$VERSION.tar.gz $ARCHNAME

echo "=> $ARCHNAME"
