from distutils.core import setup
import py2exe

import sys
#sys.path.append('C:/Program Files (x86)/Common Files/Microsoft Shared/VSTO/10.0')
sys.path.append('../epubia/Microsoft.VC90.CRT')
from glob import glob
 
includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll', 'w9xpopen.exe']

import os
templ_files = []
for root, dirs, files in os.walk('template'):
    flist = []
    for fname in files:
	flist.append(os.path.join(root, fname))
    templ_files.append( (root, flist) )
 
setup(
    windows=[{'script':'gui.py',
	      'dest_base':'cbz2epub3',
	     }],
    data_files=templ_files+
               [("Microsoft.VC90.CRT", glob('../epubia/Microsoft.VC90.CRT/*.*')),
               ],
    zipfile=None,
    options = {"py2exe": {"compressed": 2,
                          "optimize": 2,
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 1,
                          "dist_dir": "dist",
                          "xref": False,
                          "skip_archive": False,
                          "ascii": False,
                          "custom_boot_script": '',
                         }
              }
)
#vim:ts=4:sw=4:et
