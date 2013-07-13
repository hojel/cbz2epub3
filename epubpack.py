#!/bin/env python
# ePUB packaging
# (part of epubia.googlecode.com)

import os
import zipfile

def epub_archive(arg, wdir, files):
    root,epub = arg
    rdir = os.path.relpath(wdir,root)
    if wdir is root and 'mimetype' in files:
        epub.write(os.path.join(wdir,'mimetype'), 'mimetype')
        files.remove('mimetype')
    for fname in files:
        #print rdir+' -> '+fname
        file2 = fname.decode('euc-kr')
        if fname.endswith('.xhtml') or fname.endswith('.css') or fname.endswith('xpgt'):
            epub.write(os.path.join(wdir,fname), os.path.join(rdir,file2), zipfile.ZIP_DEFLATED)
        else:
            epub.write(os.path.join(wdir,fname), os.path.join(rdir,file2))

def epubpack(srcdir, outfile):
    epub = zipfile.ZipFile(outfile,'w')
    os.path.walk(srcdir, epub_archive, (srcdir,epub))
    epub.close()

if __name__=="__main__":
    epubpack('epub','out.epub')

# vim:ts=4:sw=4:et
