#!/bin/bash

PREFIX=/usr/local

if [ ! -f install.sh ] || [ ! -f img2epub.in ]; then
    echo 1>&2 "install.sh must be launch from the install directory"
    exit 1
fi

IFS='
'
rm -f $(find . -name '*~')
unset IFS

mkdir -p         ${PREFIX}/share/img2epub/data/OEBPS/images
cp -rf data      ${PREFIX}/share/img2epub/
cp -rf lib       ${PREFIX}/share/img2epub/
cp -rf VERSION   ${PREFIX}/share/img2epub/
cp -rf README    ${PREFIX}/share/img2epub/
find 2>/dev/null ${PREFIX}/share/img2epub/ -name '.svn' -exec rm -rf \{\} \;

chmod +x \
    ${PREFIX}/share/img2epub/lib/*.sh \
    ${PREFIX}/share/img2epub/lib/*.sed

VERSION=$(cat VERSION)
sed -e "s+@PREFIX@+${PREFIX}+" \
    -e "s+@VERSION@+${VERSION}+" \
    img2epub.in > \
    ${PREFIX}/bin/img2epub
chmod 755 ${PREFIX}/bin/img2epub

cat <<EOF

${PREFIX}/bin/img2epub $VERSION installed !

You should add ${PREFIX}/bin in your PATH if not already done.

img2epub --help for more information

EOF
