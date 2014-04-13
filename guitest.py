__author__ = 'alb4dx'

import wx, wx.html
import sys
import rtmidi_python as rtmidi

from leap_midi import *

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
        self.music_app = LeapMusicApp()
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
        ports = ["[None]"]
        for port_name in rtmidi.MidiOut().ports:
            ports.append(port_name)
        midi_combo = wx.ComboBox(panel, wx.ID_ANY, choices=ports)
        if len(ports) > 0:  # TODO make this dropdown actually set stuff
            evt = wx.CommandEvent(wx.EVT_COMBOBOX.typeId, winid=wx.ID_ANY)
            evt.SetInt(len(ports)-1)
            wx.PostEvent(midi_combo,evt)
            midi_combo.SetStringSelection(ports[-1])
        midi_combo.SetEditable(False)
        midi_combo.Bind(wx.EVT_COMBOBOX, self.OnMidiCombo)
        lol = self.WithHorizontalLabel(panel, midi_combo, "MIDI Out:")
        header.Add(lol, 0, wx.ALL, 0)
        testing = wx.StaticText(panel, wx.ID_ANY, "Testing?!")
        header.Add(testing, flag=wx.ALIGN_CENTER_VERTICAL)
        box.Add(header)

        axes = ["[None]","X","Y","Z","Pitch","Roll","Yaw"]
        axis_names = ["","x","y","z","pitch","roll","yaw"]
        options = ["Note","Velocity","Controller 1","Controller 2","Controller 3","Controller 4"]
        columns = ["MIDI","Axis","MIDI Min","MIDI Max"]

        axis_box = wx.GridBagSizer(vgap=0,hgap=10)

        for j in range(0,len(columns)):
            col = columns[j]
            title = self.GenDefaultLabel(panel,col)
            axis_box.Add(title, wx.GBPosition(0,j),flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        for i in range(0,len(options)):
            out = options[i]
            y = i+1

            def OnComboChange(x):
                # get AXIS from NUMBER
                # get FUNCTION from NAME
                obj = x.GetEventObject()
                axis = axis_names[x.GetInt()]
                name = obj.GetName()
                if name == options[0]:
                    setAxis_note(axis)
                elif name == options[1]:
                    setAxis_velocity(axis)
                elif name == options[2]:
                    setAxis_controller1(axis)
                elif name == options[3]:
                    setAxis_controller2(axis)
                elif name == options[4]:
                    setAxis_controller3(axis)
                elif name == options[5]:
                    setAxis_controller4(axis)


            def OnMinChange(x):
                # get FUNCTION from NAME
                obj = x.GetEventObject()
                val = x.GetInt()
                name = obj.GetName()
                if name == options[0]:
                    global range_note
                    range_note[0] = val
                elif name == options[1]:
                    global range_velocity
                    range_velocity[0] = val
                elif name == options[2]:
                    global range_controller1
                    range_controller1[0] = val
                elif name == options[3]:
                    global range_controller2
                    range_controller2[0] = val
                elif name == options[4]:
                    global range_controller3
                    range_controller3[0] = val
                elif name == options[5]:
                    global range_controller4
                    range_controller4[0] = val

            #TODO max is always one short

            def OnMaxChange(x):
                # get FUNCTION from NAME
                obj = x.GetEventObject()
                val = x.GetInt()
                name = obj.GetName()
                if name == options[0]:
                    global range_note
                    range_note[1] = val
                elif name == options[1]:
                    global range_velocity
                    range_velocity[1] = val
                elif name == options[2]:
                    global range_controller1
                    range_controller1[1] = val
                elif name == options[3]:
                    global range_controller2
                    range_controller2[1] = val
                elif name == options[4]:
                    global range_controller3
                    range_controller3[1] = val
                elif name == options[5]:
                    global range_controller4
                    range_controller4[1] = val


            label = self.GenDefaultLabel(panel,out)
            dropdown = wx.ComboBox(panel, wx.ID_ANY, choices=axes)
            dropdown.SetEditable(False)
            dropdown.Bind(wx.EVT_COMBOBOX, OnComboChange)
            dropdown.SetName(out)
            spin_style = wx.SP_ARROW_KEYS

            min_num = wx.SpinCtrl(panel, wx.ID_ANY, min=0,max=127,
                initial=0, value="0", style=spin_style)
            min_num.SetName(out)
            min_num.Bind(wx.EVT_SPINCTRL, OnMinChange)

            max_num = wx.SpinCtrl(panel, wx.ID_ANY, min=0,max=127,
                initial=127, value="127", style=spin_style)
            max_num.SetName(out)
            max_num.Bind(wx.EVT_SPINCTRL, OnMaxChange)

            flag = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL
            axis_box.Add(label, wx.GBPosition(y,0),flag=flag)
            axis_box.Add(dropdown, wx.GBPosition(y,1),flag=flag)
            axis_box.Add(min_num, wx.GBPosition(y,2),flag=flag)
            axis_box.Add(max_num, wx.GBPosition(y,3),flag=flag)

            if "Controller" in out:

                def OnControllerChange(x):
                    # get FUNCTION from NAME
                    obj = x.GetEventObject()
                    val = x.GetInt()
                    name = obj.GetName()
                    if name == options[2]:
                        setCtrlPort1(val)
                    elif name == options[3]:
                        setCtrlPort2(val)
                    elif name == options[4]:
                        setCtrlPort3(val)
                    elif name == options[5]:
                        setCtrlPort4(val)


                ctrl_num = wx.SpinCtrl(panel, wx.ID_ANY, min=0,max=127,
                    initial=0, value="0", style=spin_style)
                ctrl_num.SetName(out)
                ctrl_num.Bind(wx.EVT_SPINCTRL, OnControllerChange)
                axis_box.Add(ctrl_num, wx.GBPosition(y,4), flag=flag)

        box.Add(axis_box)

        panel.SetSizer(box)
        panel.Layout()

        # ACTUALLY START APP
        self.music_app.start()

    def GenDefaultLabel(self,window,text):
        label_text = wx.StaticText(window, wx.ID_ANY, text)
        label_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        return label_text

    def WithHorizontalLabel(self,window,thing,label):
        box = wx.BoxSizer(wx.HORIZONTAL)
        label_text = self.GenDefaultLabel(window,label)
        box.Add(label_text, proportion=0,
            flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=0)
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
            self.music_app.done = True

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

app = wx.App(redirect=False)   # Error messages go to popup window
top = AppFrame("Leap Music")
top.SetDimensions(44,44,1100,600)
top.Show()
app.MainLoop()