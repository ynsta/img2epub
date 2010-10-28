#!/bin/bash

if [ "$PREFIX" == "" ]; then
    PREFIX=/usr/local
fi

rm -rvf ${PREFIX}/share/img2epub
rm -vf  ${PREFIX}/bin/img2epub
