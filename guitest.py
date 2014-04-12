import wx, wx.html
import sys
import rtmidi_python as rtmidi

aboutText = """
<h1>Leap Music</h1>
<p>Entry for hack.uva 2014</p>
<h2>Team</h2>
<ul>
	<li>Tanya Art</li>
	<li>Andy Barron</li>
	<li>Nick Grigorian</li>
	<li>Craig Hunter</li>
</ul
"""

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About Leap Music",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, wx.ID_ANY, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class AppFrame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,200))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        # menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        # m_text = wx.StaticText(panel, wx.ID_ANY, "Hello World!")
        # m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        # m_text.SetSize(m_text.GetBestSize())
        # box.Add(m_text, 0, wx.ALL, 10)

        # m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        # m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        # box.Add(m_close, 0, wx.ALL, 10)

        header = wx.BoxSizer(wx.HORIZONTAL)
        ports = []
        for port_name in rtmidi.MidiOut().ports:
    		ports.append(port_name)
        midi_combo = wx.ComboBox(panel, wx.ID_ANY, choices=ports)
        if len(ports) > 0:
        	evt = wx.CommandEvent(wx.EVT_COMBOBOX.typeId, winid=wx.ID_ANY)
        	evt.SetInt(len(ports)-1)
        	midi_combo.SetValue(ports[-1])
        	wx.PostEvent(midi_combo,evt)
        midi_combo.SetEditable(False)
        midi_combo.Bind(wx.EVT_COMBOBOX, self.OnMidiCombo)
        lol = self.WithHorizontalLabel(panel, midi_combo, "MIDI Out:")
        header.Add(lol, 0, wx.ALL, 0)
        testing = wx.StaticText(panel, wx.ID_ANY, "Testing?!")
        header.Add(testing, flag=wx.ALIGN_CENTER_VERTICAL)
        box.Add(header)

        panel.SetSizer(box)
        panel.Layout()

    def WithHorizontalLabel(self,window,thing,label):
    	box = wx.BoxSizer(wx.HORIZONTAL)
    	label_text = wx.StaticText(window, wx.ID_ANY, label)
    	label_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
    	box.Add(label_text, proportion=0,
    		flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
    		border=10)
    	box.Add(thing, proportion=0,
    		flag=wx.ALIGN_CENTER_VERTICAL,
    		border=0)
    	return box

    def OnMidiCombo(self, arg):
    	print arg.GetInt()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

app = wx.App(redirect=False)   # Error messages go to popup window
top = AppFrame("Leap Music")
top.Show()
app.MainLoop()