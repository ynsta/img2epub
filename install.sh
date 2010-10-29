#!/bin/bash

if [ "$PREFIX" == "" ]; then
    PREFIX=/usr/local
fi

if [ ! -f install.sh ] || [ ! -f img2epub ]; then
    echo 1>&2 "install.sh must be launch from the install directory"
    exit 1
fi

mkdir -p           ${PREFIX}/bin
mkdir -p           ${PREFIX}/share/img2epub/lib
cp -vf lib/*.py    ${PREFIX}/share/img2epub/lib
cp -vf img2epub    ${PREFIX}/share/img2epub
cp -vf README      ${PREFIX}/share/img2epub

cat <<EOF > ${PREFIX}/bin/img2epub
#!$(which python) ${PREFIX}/share/img2epub/img2epub
EOF
chmod 755 ${PREFIX}/bin/img2epub

cat <<EOF

$(${PREFIX}/bin/img2epub --version)

installed !

You should add ${PREFIX}/bin in your PATH if not already done.

img2epub --help for more information

EOF
