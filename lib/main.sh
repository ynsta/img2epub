#!/usr/bin/true

if   [ -f "${INPUT}" ] && [ ! -d "${INPUT}" ] && [ "${INPUT}" != "${INPUT/.cbz/}" ]; then

    IMGDIR="${INPUT/.cbz/}_${RANDOM}"
    7z x -y "${INPUT}" -o"${IMGDIR}"
    RMDIR=1
    sync
    sleep 1

elif [ -f "${INPUT}" ] && [ ! -d "${INPUT}" ] && [ "${INPUT}" != "${INPUT/.cbr/}" ]; then

    IMGDIR="${INPUT/.cbr/}_${RANDOM}"
    7z x -y "${INPUT}" -o"${IMGDIR}"
    RMDIR=1
    sync
    sleep 1

elif [ -d "$INPUT" ]; then

    IMGDIR="${INPUT}"
    RMDIR=0

else
    exit 2
fi

if [ ! -d "${IMGDIR}" ]; then
    exit 1
fi

#
# =====================================================================
function epub_name() {
    echo "${GOPT__CREATOR}__${GOPT__TITLE}__${GOPT__LANGUAGE}" | \
	sed \
	-e 's/, /,/g' \
	-e 's/ /_/g' \
	-e 's/[^a-zA-Z0-9,_ -]//g' | \
	sed -f $PREFIX/share/img2epub/lib/strip-utf8.sed
}

# Tempory Files and Directories Creation
# =====================================================================
LAUNCHDIR=$(pwd)
cd "${IMGDIR}"
IMGDIR=$(pwd)
cd ..
if [ "${GOPT__OUTPUT}" != "" ]; then
    cd "${LAUNCHDIR}"
    EPUB="${GOPT__OUTPUT%.epub}"
else
    EPUB=$(epub_name)
fi
EPUBDIR="${EPUB}_${RANDOM}"
mkdir -p "${EPUBDIR}"
cd "${EPUBDIR}"
EPUBDIR="$(pwd)"
cd "${LAUNCHDIR}"

cp -rf $PREFIX/share/img2epub/data/* "${EPUBDIR}"

LIST0=/tmp/list${RANDOM}.txt
LIST1=/tmp/list${RANDOM}.txt
LIST2=/tmp/list${RANDOM}.txt
LISTC=/tmp/list${RANDOM}.txt

rm -f $LIST0 $LIST1 $LIST2 $LISTC
touch $LIST0
touch $LIST1
touch $LIST2
touch $LISTC

# Images Pre Processing
# =====================================================================
find ${IMGDIR} -iname '*.jpg' -or -iname '*.png' -or -iname '*.bmp' -or -iname '*.gif' | sort -g > $LIST0

IFS='
'
C=0;N=0;
for i in $(cat $LIST0); do
    if [ "$CYGWIN" = "1" ]; then
	cygpath -aw "$i" >> $LIST1
    else
	echo "$i" >> $LIST1
    fi

    cdir=$(dirname $i)
    if [ "$cdir" != "$odir" ]; then
	C=$((C+1))
	echo "$C:$N" >> $LISTC
    fi
    odir=$cdir
    N=$((N+1))
done

cd "${EPUBDIR}/OEBPS/images"

CONVERT_OPT=""
if [ "$GOPT__NOTRIM" != "1" ] && [ $GOPT__TRIM_ITER -gt 0 ] ; then
    N=0; while [ $N -lt $GOPT__TRIM_ITER ]; do
	CONVERT_OPT="${CONVERT_OPT}
-fuzz
${GOPT__TRIM_VAL}%
-trim"
	N=$((N+1))
    done
    CONVERT_OPT="${CONVERT_OPT}
+repage"
fi

if [ "$GOPT__DITHER" != "1" ]; then
    CONVERT_OPT="${CONVERT_OPT}
+dither"
else
    CONVERT_OPT="${CONVERT_OPT}
-dither"
fi

N=0;
for img in $(cat $LIST1); do

    w=0
    h=0
    retry=10
    while [ $w -eq 0 ] || [ $h -eq 0 ]; do
        temp=$(identify -format '%w:%h' "${img}" | sed -e '1,1s/[^0-9:]//g')
	printf -v w '%d' ${temp%:*}
	printf -v h '%d' ${temp#*:}

	if [ $w -eq 0 ] || [ $h -eq 0 ]; then
	    sleep 1;
	fi

	retry=$((retry - 1))
	if [ $retry -le 0 ]; then
	    break
	fi
    done

    echo -n "Pre processing $img"
    echo -n " (${w}x${h}) ... "

    if  ([ "$GOPT__CUT" = "A" ])                  ||
	([ "$GOPT__CUT" = "H" ] && [ $w -gt $h ]) ||
	([ "$GOPT__CUT" = "R" ] && [ $w -gt $h ]) ||
	([ "$GOPT__CUT" = "V" ] && [ $w -lt $h ])
    then
	tmp=tmp_${RANDOM}

	echo -n "(cut) "

	convert "$img" \
	    -rotate '-90<' -crop '50,100%' \
	    -type Grayscale -quantize Gray \
	    -normalize \
	    -level 8%,92%,1.2} \
	    $CONVERT_OPT \
	    -resize ${GOPT__HSIZE}x${GOPT__VSIZE} \
	    -normalize \
	    -colors ${GOPT__COLORS} \
	    -normalize \
	    ${tmp}.png

	printf -v NLF "%08d" $N;
	if [ "$GOPT__CUT" = "R" ]; then
	    mv ${tmp}-1.png ${NLF}.png
	else
	    mv ${tmp}-0.png ${NLF}.png
	fi
	echo ${NLF}.png >> $LIST2

	NUMBERS[$N]=${NLF}
	N=$((N+1))

	printf -v NLF "%08d" $N;
	if [ "$GOPT__CUT" = "R" ]; then
	    mv ${tmp}-0.png ${NLF}.png
	else
	    mv ${tmp}-1.png ${NLF}.png
	fi
	echo ${NLF}.png >> $LIST2

	NUMBERS[$N]=${NLF}
	N=$((N+1))

	rm -f ${tmp}-*.png;
    else
	printf -v NLF "%08d" $N

	convert "$img" \
	    -rotate '+90>' \
	    -type Grayscale -quantize Gray \
	    -normalize \
	    -level 8%,92%,1.2 \
	    $CONVERT_OPT \
	    -resize ${GOPT__HSIZE}x${GOPT__VSIZE} \
	    -normalize \
	    -colors ${GOPT__COLORS} \
	    -normalize \
	    ${NLF}.png

	echo ${NLF}.png >> $LIST2

	NUMBERS[$N]=${NLF}
	N=$((N+1))
    fi
    echo "done"
done


if [ "$RMDIR" = "1" ]; then
    rm -rf ${IMGDIR}
fi

# EPUB Contents Creation
# =====================================================================
function replace_tags() {
    for file; do
	sed -i \
	    -e s/"@TITLE@"/"${GOPT__TITLE}"/g \
	    -e s/"@CREATOR@"/"${GOPT__CREATOR}"/g \
	    -e s/"@LANGUAGE@"/"${GOPT__LANGUAGE}"/g \
	    -e s/"@PUBLISHER@"/"${GOPT__PUBLISHER}"/g \
	    -e s/"@DATE@"/"${GOPT__DATE}"/g \
	    -e s/"@SUBJECT@"/"${GOPT__SUBJECT}"/g \
	    -e s/"@TYPE@"/"${GOPT__TYPE}"/g \
	    -e s/"@UUID@"/"${GOPT__UUID}"/g \
	    "$file"
    done
}

replace_tags \
    "${EPUBDIR}"/OEBPS/content.ncx \
    "${EPUBDIR}"/OEBPS/content.opf \
    "${EPUBDIR}"/OEBPS/title.xml \
    "${EPUBDIR}"/OEBPS/@NUMBER@.xml

N=0; for i in $(cat $LIST2); do
    NUMBER=${NUMBERS[$N]}
    cp "${EPUBDIR}/OEBPS/@NUMBER@.xml" "${EPUBDIR}/OEBPS/${NUMBER}.xml"
    sed -i -e s/"@NUMBER@"/"${NUMBER}"/g "${EPUBDIR}/OEBPS/${NUMBER}.xml"
    N=$((N+1))
done
rm "${EPUBDIR}/OEBPS/@NUMBER@.xml"


# EPUB Items and Navigation Points Creation
# =====================================================================
for NUMBER in "${NUMBERS[@]}"; do
    cat <<EOF >> "${EPUBDIR}"/OEBPS/content.opf
    <item id="xml_${NUMBER}" href="${NUMBER}.xml" media-type="application/xhtml+xml"/>
    <item id="png_${NUMBER}" href="images/${NUMBER}.png" media-type="image/png"/>
EOF
done

cat  <<EOF >> "${EPUBDIR}"/OEBPS/content.opf
  </manifest>
  <spine toc="ncx">
    <itemref idref="title" />
EOF
for NUMBER in "${NUMBERS[@]}"; do
    cat <<EOF >> "${EPUBDIR}"/OEBPS/content.opf
    <itemref idref="xml_${NUMBER}" />
EOF
done
cat  <<EOF >> "${EPUBDIR}"/OEBPS/content.opf
  </spine>
</package>
EOF


# EPUB Table of Contents Creation
# =====================================================================
N=2;
for c in $(cat $LISTC); do
    CHAP=${c/:*/}
    NUMB=${c/*:/}
    NUMBER=${NUMBERS[$NUMB]}
    echo "CHAP=${CHAP}, NUMB=${NUMB}, NUMBER=${NUMBER}"


    cat <<EOF >> "${EPUBDIR}"/OEBPS/content.ncx
    <navPoint id="xml_${NUMBER}" playOrder="${N}"> <navLabel><text>Chapter ${CHAP}</text></navLabel><content src="${NUMBER}.xml"/></navPoint>
EOF
    N=$((N+1))
done

cat <<EOF >> "${EPUBDIR}"/OEBPS/content.ncx
  </navMap>
</ncx>
EOF


# EPUB Container Creation
# =====================================================================
cd "${EPUBDIR}"

7z a -y -tzip -mm=Copy -mx=0 -scsUTF-8 "${EPUB}".zip mimetype
7z a -y -tzip -mm=Copy -mx=0 -scsUTF-8 "${EPUB}".zip META-INF
7z a -y -tzip -mm=Copy -mx=0 -scsUTF-8 "${EPUB}".zip OEBPS

mv "${EPUB}".zip ../"${EPUB}".epub

# Temporary Files and Directories Cleaning
# =====================================================================
cd ${LAUNCHDIR}
rm -f $LIST0 $LIST1 $LIST2 $LISTC

n=0;
while ! rm -rf ${EPUBDIR} &>/dev/null; do
    sync
    sleep 1
    n=$((n+1))
    if [ $n -gt 10 ]; then
	break;
    fi
done


#àáâãäçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ
#aaaaaceeeeiiiinooooouuuuyyAAAAACEEEEIIIINOOOOOUUUUY
