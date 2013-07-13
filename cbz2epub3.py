#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generate ePUB structure
#   1. extract image files from ZIP to temp directory
#       - natural sort
#       - consider directory name as episode(or book) name
#       - rename all files (c#p# format)
#       - determine split or not
#           c#p# -> c#p#a & c#p#b
#   2. generate ePUB tree
#       - copy files from template to output dir
#       - replace
#   3. generate wrapper
#       - move image files to output dir 
#       - generate wrapper XHTML
#   4. make ePUB
#
import os
import re
import shutil
import zipfile
import tempfile
from natsort import natsorted
from epubpack import epubpack
from PIL import Image
import uuid

def cbz2epub3(cbzfname, epubfile='out.eub', tmpldir='template', mangamode=False, singlepage=False):
    # working dir
    imgdir = tempfile.mkdtemp()
    workdir = tempfile.mkdtemp()
    # convert
    img_files = importImageFromZip(cbzfname, imgdir, mangamode=mangamode, singlepage=singlepage)
    title = guessTitle(cbzfname)
    ttbl = genTemplateInfo(img_files, title, mangamode=mangamode)
    epubMakeTree(tmpldir, workdir, ttbl)
    for fname in os.listdir(imgdir):
        shutil.move(os.path.join(imgdir, fname), os.path.join(workdir, 'EPUB', 'Image'))
    epubpack(workdir, epubfile)
    # cleanup
    os.rmdir(imgdir)
    shutil.rmtree(workdir)

def importImageFromZip(cbzfname, outdir, mangamode=False, singlepage=False):
    # extract
    cbz = zipfile.ZipFile(cbzfname,'r')
    fnames = cbz.namelist()
    cbz.extractall(outdir)
    cbz.close()
    # change name
    print "Src images: %d" % len(fnames)
    nlenw = len(str(len(fnames)))
    new_fnames = []
    idx = 0
    for fname in natsorted(fnames):
        ext = os.path.splitext(fname)[1]
        src = os.path.join(outdir, fname)
        if fname == 'Thumbs.db':
            os.remove(src)
            continue
        idx += 1
        im = Image.open(src)
        width, height = im.size
        is_wide = width > height
        if singlepage and is_wide:
            # ask to use 'briss' to get better result
            half = int(width/2)
            pt = im.crop( (0, 0, half, height) )
            new_fname = "img{1:0{0:d}d}{3:s}{2:s}".format(nlenw, idx, ext, 'b' if mangamode else 'a')
            dst = os.path.join(outdir, new_fname)
            pt.save(dst, 'jpeg')
            new_fnames.append( new_fname )
            pt = im.crop( (half+1, 0, width, height) )
            new_fname = "img{1:0{0:d}d}{3:s}{2:s}".format(nlenw, idx, ext, 'a' if mangamode else 'b')
            dst = os.path.join(outdir, new_fname)
            pt.save(dst, 'jpeg')
            del im
            os.remove(src)
            new_fnames.append( new_fname )
        else:
            if is_wide:
                new_fname = "img{1:0{0:d}d}w{2:s}".format(nlenw, idx, ext)
            else:
                new_fname = "img{1:0{0:d}d}{2:s}".format(nlenw, idx, ext)
            dst = os.path.join(outdir, new_fname)
            del im
            shutil.move(src, dst)
            new_fnames.append( new_fname )
    print "Dst images: %d" % len(new_fnames)
    return new_fnames

def guessTitle(filename):
    title = os.path.splitext(os.path.basename(filename))[0]
    return title.replace('_', ' ').encode('utf-8')

def genTemplateInfo(imgfiles, title='Unknown', mangamode=False):
    # generate template info from file list
    ttbl = {
        'TITLE' : title,
        'DIRECTION' : 'ltr',
        'FILELIST' : [],
        'ITEMREFLIST' : [],
        'PAGELIST' : [],
        'IMGFILELIST' : [],
    }
    ptn_num = re.compile('(\d+)')
    ttbl['ID'] = 'urn:uuid:'+str(uuid.uuid4())
    if mangamode:
        ttbl['DIRECTION'] = 'rtl'
    for fname in imgfiles:
        bname = os.path.splitext(fname)[0]
        pnum = ptn_num.search(bname).group(1)
        #
        if int(pnum) == 1:
            ttbl['COVERID'] = bname
            ttbl['FILELIST'].append('<item id="{0:s}" href="Image/{0:s}.jpg" media-type="image/jpeg" properties="cover-image"/>'.format(bname))
        else:
            ttbl['FILELIST'].append('<item id="{0:s}" href="Image/{0:s}.jpg" media-type="image/jpeg"/>'.format(bname))
        ttbl['FILELIST'].append('<item id="_{0:s}" href="Content/{0:s}.xhtml" media-type="application/xhtml+xml"/>'.format(bname))
        #
        if bname.endswith('w'):
            ttbl['ITEMREFLIST'].append('<itemref idref="_{0:s}" properties="rendition:page-spread-center"/>'.format(bname))
        elif bname.endswith('a'):
            ttbl['ITEMREFLIST'].append('<itemref idref="_{0:s}" properties="rendition:spread-both page-spread-{1:s}"/>'.format(bname, 'right' if mangamode else 'left'))
        elif bname.endswith('b'):
            ttbl['ITEMREFLIST'].append('<itemref idref="_{0:s}" properties="rendition:spread-both page-spread-{1:s}"/>'.format(bname, 'left' if mangamode else 'right'))
        else:
            ttbl['ITEMREFLIST'].append('<itemref idref="_{0:s}"/>'.format(bname))
        #
        if not bname.endswith('b'):
            ttbl['PAGELIST'].append('<li><a href="../Content/{0:s}.xhtml">{1:d}</a></li>'.format(bname, int(pnum)))
        ttbl['IMGFILELIST'].append(fname)
    return ttbl

def epubMakeTree(tmpldir, outdir, ttbl):
    # copy epub directory
    for root, dirs, files in os.walk(tmpldir):
        sdir = os.path.relpath(root, tmpldir)
        new_root = os.path.join(outdir, sdir)
        if os.path.normpath(new_root) != outdir:
            os.makedirs(new_root)
        for fn in files:
            src = os.path.join(root, fn)
            if fn.startswith('__'):
                keywd, ext = os.path.splitext(os.path.basename(fn))
                keywd = keywd[2:]
                if not keywd.endswith('LIST'):
                    print "ERROR: template name should end with LIST"
                for name in ttbl[keywd]:
                    nname = os.path.splitext(name)[0]+ext
                    dst = os.path.join(new_root, nname)
                    ttbl[keywd[:-4]] = name
                    filtcopy(src, dst, ttbl)
            else:
                dst = os.path.join(new_root, fn)
                ext = os.path.splitext(fn)[1]
                if ext in ['.opf', '.xhtml']:
                    filtcopy(src, dst, ttbl)
                else:
                    shutil.copy(src, dst)

def filtcopy(src, dst, ttbl):
    tmpl = open(src, 'r').read()
    doc = tmpl
    for spc, keywd in re.compile('^(.*)@@@([A-Z]+)@@@', re.M).findall(tmpl):
        if not keywd in ttbl:
            print "ERROR: no keyword found, "+keywd+", at "+src
        if keywd.endswith('LIST'):
            ll = [spc+val for val in ttbl[keywd]]
            doc = doc.replace(spc+'@@@'+keywd+'@@@', '\n'.join(ll))
        else:
            doc = doc.replace('@@@'+keywd+'@@@', ttbl[keywd])
    open(dst, 'w').write(doc)

if __name__ == "__main__":
    #cbz2epub3('test1.zip', 'test1.epub')
    cbz2epub3('test2.zip', 'test2.epub', mangamode=True)
    """
    imgdir = 'img'
    workdir = 'epub'
    #img_files = importImageFromZip('test1.zip', imgdir)
    img_files = []
    for root, dirs, files in os.walk('img'):
        for fname in files:
            img_files.append( fname )
    print len(img_files)

    ttbl = genTemplateInfo(img_files, title='십이국기 1')
    epubMakeTree('template', workdir, ttbl)

    for fname in os.listdir('img'):
        shutil.copy(os.path.join('img', fname), os.path.join(workdir, 'EPUB', 'Image'))
    """

# vim:ts=4:sw=4:et
