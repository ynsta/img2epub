#!/bin/bash

if [ ! -f install.sh ] || [ ! -f img2epub ]; then
    echo 1>&2 "install.sh must be launch from the install directory"
    exit 1
fi

VERSION=$(python img2epub --version | head -n 1 | cut -d ' ' -f 2)
mkdir -p ../img2epub-$VERSION
cp -rf *  ../img2epub-$VERSION
opwd="${PWD}"
cd ..

tar --exclude=.svn -czf img2epub-$VERSION.tgz img2epub-$VERSION
md5sum img2epub-$VERSION.tgz > img2epub-$VERSION.md5

cd "$opwd"
rm -rf ../img2epub-$VERSION
