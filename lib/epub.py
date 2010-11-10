#!/bin/env python
# -*- coding: utf8 -*-

import os
import tempfile
import binutils
import shutil

mimetype  = ('mimetype',
             'application/epub+zip\n')

container = (os.path.join('META-INF', 'container.xml'),
             '''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
''')


main_css = (os.path.join('OEBPS', 'css', 'main.css'),
            '''body {
    background-color: #FFFFFF;
    color:            #000000;
    text-align:       center;
    padding:          0px;
    margin:           2px
}

img {
    padding:          0px;
    margin:           0px;
    border:           0px
}

h1 {
    font-size:        1.4em;
    font-weight:      bold
}

h2 {
    font-size:        1.0em;
}

div.title {
    padding-top:      25%;
    text-align:       center;
    font-family:      serif
}
div.infos {
    padding-top:      20px;
    padding-right:    30px;
    font-size:        0.6em;
    text-align:       right;
    font-family:      sans-serif
}
''')

def content_ncx(opts, chapter_list, chapter_map, image_list):
    fname = os.path.join('OEBPS', 'content.ncx')
    data  = '''<?xml version="1.0" encoding="UTF-8" ?>

<!DOCTYPE ncx PUBLIC
	  "-//NISO//DTD ncx 2005-1//EN"
	  "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx version="2005-1"
     xml:lang="fr"
     xmlns="http://www.daisy.org/z3986/2005/ncx/">

  <head>
    <meta name="dtb:uid" content="%s"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>

  <docTitle><text>%s</text></docTitle>

  <docAuthor><text>%s</text></docAuthor>

  <navMap>
    <navPoint id="title" playOrder="1">
      <navLabel><text>Title</text></navLabel>
      <content src="title.xml"/>
    </navPoint>
''' % (opts.uuid, opts.title, opts.creator)
    for i in range(len(chapter_list)):
        cname = chapter_list[i]
        data = data + '''    <navPoint id="xml_%s" playOrder="%d">
      <navLabel><text>%s</text></navLabel>
      <content src="%s.xml"/>
    </navPoint>
''' % (image_list[chapter_map[cname][0]],
       i + 2,
       cname,
       image_list[chapter_map[cname][0]])
    data = data + '''  </navMap>
</ncx>'''
    return (fname, data)



def content_opf(opts, image_list):
    fname = os.path.join('OEBPS', 'content.opf')
    data = '''<?xml version="1.0" encoding="UTF-8" ?>
<package version="2.0"
	 unique-identifier="PrimaryID"
	 xmlns="http://www.idpf.org/2007/opf">

  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
	    xmlns:opf="http://www.idpf.org/2007/opf"
	    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <dc:identifier id="PrimaryID">urn:uuid:%s</dc:identifier>
    <dc:title>%s</dc:title>
    <dc:language>%s</dc:language>
    <dc:creator opf:file-as="%s">%s</dc:creator>
    <dc:publisher>%s</dc:publisher>
    <dc:description></dc:description>
    <dc:coverage></dc:coverage>
    <dc:source></dc:source>
    <dc:date>%s</dc:date>
    <dc:subject>%s</dc:subject>
    <dc:type>%s</dc:type>
    <dc:rights></dc:rights>

  </metadata>

  <manifest>

    <item id="title" href="title.xml" media-type="application/xhtml+xml"/>
    <item id="css_main" href="css/main.css" media-type="text/css"/>
    <item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
''' % (opts.uuid,
       opts.title,
       opts.language,
       opts.creator,
       opts.creator,
       opts.publisher,
       opts.date,
       opts.subject,
       opts.type)

    for i in image_list:
        data = data + '''    <item id="xml_%s" href="%s.xml" media-type="application/xhtml+xml"/>
    <item id="png_%s" href="images/%s.png" media-type="image/png"/>
''' % (i,i,i,i)

    data = data + '''  </manifest>
  <spine toc="ncx">
    <itemref idref="title" />
'''
    for i in image_list:
        data = data + '    <itemref idref="xml_%s" />\n' % (i)
    data = data + '''  </spine>
</package>
'''
    return (fname, data)


def title_xml(opts):
    fname = os.path.join('OEBPS', 'title.xml')
    data = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC
	  "-//W3C//DTD XHTML 1.1//EN"
	  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="%s">
  <head>
    <meta http-equiv="Content-Type"
	  content="application/xhtml+xml; charset=utf-8" />
    <title>%s</title>
    <link rel="stylesheet" href="css/main.css" type="text/css" />
  </head>
  <body>
    <div class="infos">
      %s %s<br />
      %s<br />
    </div>
    <div class="title">
      <h1>%s</h1>
      <h2>%s</h2>
    </div>
  </body>
</html>
''' % (opts.language,
       opts.title,
       opts.publisher,
       opts.date,
       opts.type,
       opts.title,
       opts.creator)
    return (fname, data)

def image_xml(image):
    fname = os.path.join('OEBPS', image + '.xml')
    data = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC
	  "-//W3C//DTD XHTML 1.1//EN"
	  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="@LANG@">
  <head>
    <meta http-equiv="Content-Type"
	  content="application/xhtml+xml; charset=utf-8" />
    <title>%s</title>
    <link rel="stylesheet" href="css/main.css" type="text/css" />
  </head>
  <body>
    <img src="images/%s.png" />
  </body>
</html>
''' % (image, image)
    return (fname, data)

def img_convert(opts, src, dst, idx, convert_opts):

    (r, s, e) = binutils.run('identify', ['-format', '%w:%h', src])

    if r != 0 or e != '':
        sys.stderr.write(e)
        (w, h) = (0, 0)
    else:
        (w, h) = s.strip().split(':')
        (w, h) = (int(w), int(h))

    name = [ dst + ('%04d' % (idx)) ]
    if opts.cut and ((opts.cut == 'A') or
                     (opts.cut == 'H' and w > h) or
                     (opts.cut == 'R' and w > h) or
                     (opts.cut == 'V' and w < h)):
        name.append(dst + ('%04d' % (idx + 1)))
        print 'Creating %s and %s from %s (%dx%d)' % (name[0], name[1], src, w, h),
        (r, s, e) = binutils.run('convert',
                                 [
                src,
                '-rotate', '-90<',
                '-crop', '50,100%',
                '-type', 'Grayscale',
                '-quantize', 'Gray',
                '-normalize',
                '-level', '8%,92%,1.2'] + convert_opts + [
                '-resize', ('%dx%d' % (opts.hsize, opts.vsize)),
                '-normalize',
                '-colors', str(opts.colors),
                '-normalize',
                'TMP.png'])
        if e: sys.stderr.write(e)
        if opts.cut == 'R':
            os.rename('TMP-1.png', os.path.join('OEBPS', 'images', name[0] + '.png'))
            os.rename('TMP-0.png', os.path.join('OEBPS', 'images', name[1] + '.png'))
        else:
            os.rename('TMP-0.png', os.path.join('OEBPS', 'images', name[0] + '.png'))
            os.rename('TMP-1.png', os.path.join('OEBPS', 'images', name[1] + '.png'))
        print 'Done'
    else:
        print 'Creating %s from %s (%dx%d)' % (name[0], src, w, h),
        (r, s, e) = binutils.run('convert',
                                 [
                src,
                '-rotate', '-90>',
                '-type', 'Grayscale',
                '-quantize', 'Gray',
                '-normalize',
                '-level', '8%,92%,1.2'] + convert_opts + [
                '-resize', ('%dx%d' % (opts.hsize, opts.vsize)),
                '-normalize',
                '-colors', str(opts.colors),
                '-normalize',
                'TMP.png'])
        if e: sys.stderr.write(e)
        os.rename('TMP.png', os.path.join('OEBPS', 'images', name[0] + '.png'))
        print 'Done'
    return name

def create_epub(opts,
                epub_name,
                image_list,
                chapter_list,
                chapter_map,
                callback = None,
                callback_arg = None):
    convert_opts = []
    if not opts.notrim and opts.trim_iter > 0:
        for i in range(opts.trim_iter):
            convert_opts = convert_opts + ['-fuzz', str(opts.trim_val) + '%' , '-trim']
    if not opts.dither:
        convert_opts = convert_opts + ['+dither']

    epub_name = os.path.abspath(epub_name)

    curdir = os.path.abspath('.')
    epubdir = tempfile.mkdtemp()
    os.chdir(epubdir)
    os.mkdir('META-INF')
    os.mkdir('OEBPS')
    os.mkdir(os.path.join('OEBPS', 'images'))
    os.mkdir(os.path.join('OEBPS', 'css'))
    open(mimetype[0],  'w+b').write(mimetype[1])
    open(container[0], 'w+b').write(container[1])
    open(main_css[0],  'w+b').write(main_css[1])

    (f, d) = title_xml(opts)
    open(f, 'w+b').write(d)

    dst_image_list = []
    dst_chapter_map = {}
    idx = 0
    for ci in range(len(chapter_list)):
        cname = chapter_list[ci]
        dst_chapter_map[cname] = []
        for ii in chapter_map[cname]:
            src_img = image_list[ii]
            for dst_img in img_convert(opts, src_img, ('C%03dI' % ci), idx, convert_opts):
                dst_chapter_map[cname].append(idx)
                dst_image_list.append(dst_img)
                (f, d) = image_xml(dst_img)
                open(f, 'w+b').write(d)
                idx = idx + 1
            if callback: callback()

    (f, d) = content_ncx(opts, chapter_list, dst_chapter_map, dst_image_list)
    open(f, 'w+b').write(d)

    (f, d) = content_opf(opts, dst_image_list)
    open(f, 'w+b').write(d)

    try:
        os.unlink(epub_name)
    except:
        None

    seven_opt = ['a', '-y', '-tzip', '-mm=Copy', '-scsUTF-8']

    (r1,s,e) = binutils.run('7z', seven_opt + ['-mx=0', epub_name, 'mimetype'])
    if e: sys.stderr.write(e)
    if r1 != 0:
        (r1,s,e) = binutils.run('7z', seven_opt[:-1] + ['-mx=0', epub_name, 'mimetype'])
        if e: sys.stderr.write(e)
    (r2,s,e) = binutils.run('7z', seven_opt + [epub_name, 'META-INF'])
    if e: sys.stderr.write(e)
    if r2 != 0:
        (r2,s,e) = binutils.run('7z', seven_opt[:-1] + [epub_name, 'META-INF'])
        if e: sys.stderr.write(e)
    (r3,s,e) = binutils.run('7z', seven_opt + [epub_name, 'OEBPS'])
    if e: sys.stderr.write(e)
    if r3 != 0:
        (r3,s,e) = binutils.run('7z', seven_opt[:-1] + [epub_name, 'OEBPS'])
        if e: sys.stderr.write(e)

    if not r1 and not r2 and not r3:
        print '\n', epub_name, 'created'

    os.chdir(curdir)
    shutil.rmtree(epubdir, ignore_errors=True)
