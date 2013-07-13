#!/usr/bin/env python
#  manga ZIP to ePUB3
__program__ = 'cbz2epub3'
__version__ = '0.1.0'

import os
from cbz2epub3 import cbz2epub3

#------------------------------------------------
# GUI
#------------------------------------------------
import wx

label_widget = None
idle_label = "Drop ePub file below"

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        self.obj.log.SetInsertionPointEnd()
        mangamode = self.obj.manga_cb.GetValue()
        singlepage = self.obj.single_cb.GetValue()

        if mangamode:
            self.obj.log.AppendText( "Manga mode\n" )
        if singlepage:
            self.obj.log.AppendText( "Single-page\n" )

        global label_widget, idle_label
        maxcnt = len(filenames)
        cnt = 0
        for filename in filenames:
            cnt += 1
            info_str = "%d / %d is processed: %s" % (cnt, maxcnt, os.path.basename(filename))
            label_widget.SetLabel(info_str)
            epubname = os.path.splitext(filename)[0]+'.epub'
            output = cbz2epub3( filename, epubname, mangamode=mangamode, singlepage=singlepage )
            self.obj.log.AppendText( u"{0:s} changed\n".format(filename) )
        label_widget.SetLabel(idle_label)

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        panel = wx.Panel(self, wx.ID_ANY)

        #--- Top button bar
        btnszer1 = wx.BoxSizer( wx.HORIZONTAL )

        # Manga select
        lbl1 = wx.StaticText(panel, label="Manga")
        self.manga_cb = wx.CheckBox(panel, wx.ID_ANY)
        btnszer1.Add( self.manga_cb, 0, wx.LEFT|wx.RIGHT, 2 )
        btnszer1.Add( lbl1, 0, wx.LEFT|wx.CENTRE|wx.RIGHT, 2 )

        # Single select
        lbl1 = wx.StaticText(panel, label="Single-page")
        self.single_cb = wx.CheckBox(panel, wx.ID_ANY)
        btnszer1.Add( self.single_cb, 0, wx.LEFT|wx.RIGHT, 2 )
        btnszer1.Add( lbl1, 0, wx.LEFT|wx.CENTRE|wx.RIGHT, 2 )

        #--- Drop zone
        global label_widget, idle_label
        tlb1 = wx.StaticText(panel, label=idle_label)
        label_widget = tlb1
        self.log = wx.TextCtrl(panel, size=(400,200),
                        style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        # set Drop zone
        self.log.SetDropTarget( FileDropTarget(self) )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btnszer1, 0, wx.GROW|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(tlb1, 0, wx.GROW|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(self.log, 1, wx.GROW|wx.ALL, 5)

        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Show(True)

def gui():
    app = wx.App(False)
    frame = MyFrame(None, __program__)
    app.MainLoop()

if __name__ == "__main__":
    # option parsing
    from optparse import OptionParser

    parser = OptionParser(usage = '%prog [options] [cbz files]')
    parser.add_option("-m", "--manga",
                      dest="manga", default=False,
                      help="Right-to-Left")
    parser.add_option("-s", "--single",
                      dest="single", default=False,
                      help="Force single page")
    options, args = parser.parse_args()

    if len(args) == 0:
        gui()
    else:
        for filename in args:
            epubname = os.path.splitext(filename)[0]+'.epub'
            cbz2epub3(filename, epubname, mangamode=options.manga, singlepage=options.single)

# vim:ts=4:sw=4:et
