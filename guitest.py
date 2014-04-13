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

        cfg_menu = wx.Menu()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menuBar.Append(menu, "&File")
        menuBar.Append(cfg_menu, "&Settings")
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
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

        footer = wx.BoxSizer(wx.HORIZONTAL)
        ports = []
        for port_name in rtmidi.MidiOut().ports:
            ports.append(port_name)
        midi_combo = wx.ComboBox(panel, wx.ID_ANY, choices=ports)
        if len(ports) > 0:
            midi_combo.Select(len(ports)-1)
            self.music_app.set_out(len(ports)-1)
        midi_combo.SetEditable(False)
        midi_combo.Bind(wx.EVT_COMBOBOX, self.OnMidiCombo)
        lol = self.WithHorizontalLabel(panel, midi_combo, "MIDI Out:")
        footer.Add(lol, 0, wx.ALL, 0)

        axes = ["[None]","X","Y","Z","Pitch","Roll","Yaw"]
        axis_names = ["","x","y","z","pitch","roll","yaw"]
        options = ["Note","Velocity","Controller 1","Controller 2","Controller 3","Controller 4"]
        columns = ["","Axis","Port","Range"]

        self.control_dict = {}

        axis_box = wx.GridBagSizer(vgap=10,hgap=10)

        for j in range(0,len(columns)):
            col = columns[j]
            title = self.GenDefaultLabel(panel,col)
            span = wx.GBSpan(1,1)
            if col == "Range":
                span = wx.GBSpan(1,2)
            axis_box.Add(title, wx.GBPosition(0,j),flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, span=span)

        label_root = self.GenDefaultLabel(panel,"Root")
        label_scale = self.GenDefaultLabel(panel,"Scale")
        label_octaves = self.GenDefaultLabel(panel,"Octaves")
        flagz = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL
        axis_box.Add(label_root, wx.GBPosition(0,len(columns)+2),flag=flagz)
        axis_box.Add(label_scale, wx.GBPosition(0,len(columns)+1),flag=flagz)
        axis_box.Add(label_octaves, wx.GBPosition(0,len(columns)+3),flag=flagz)

        roots = []
        octave = 0
        note_idx = 0
        notes = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
        for i in range(0,128-12):
            st = notes[note_idx]+str(octave)
            roots.append(st)
            note_idx += 1
            if note_idx == 12:
                note_idx = 0
                octave += 1

        root_box = wx.ComboBox(panel, wx.ID_ANY, choices=roots)
        axis_box.Add(root_box,wx.GBPosition(1,len(columns)+2),flag=flagz)

        scale_choices = ["[None]"] + constants.scale_offsets.keys()
        scale_box = wx.ComboBox(panel, wx.ID_ANY, choices=scale_choices)
        axis_box.Add(scale_box,wx.GBPosition(1,len(columns)+1),flag=flagz)

        octave_choices = []
        for i in range(1,10):
            octave_choices.append(str(i))

        octave_box = wx.ComboBox(panel, wx.ID_ANY, choices=octave_choices)
        axis_box.Add(octave_box,wx.GBPosition(1,len(columns)+3),flag=flagz)

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


            def OnMaxChange(x):
                # get FUNCTION from NAME
                obj = x.GetEventObject()
                val = x.GetInt() + 1
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

            key = "".join( out.lower().split() )

            label = self.GenDefaultLabel(panel,out)
            dropdown = wx.ComboBox(panel, wx.ID_ANY, choices=axes)
            dropdown.SetEditable(False)
            dropdown.Bind(wx.EVT_COMBOBOX, OnComboChange)
            dropdown.SetName(out)
            spin_style = wx.SP_ARROW_KEYS | wx.ALIGN_RIGHT

            range_sz = wx.Size(w=49, h=25)

            min_num = wx.SpinCtrl(panel, wx.ID_ANY, min=0,max=127,
                initial=0, value="0", style=spin_style, size=range_sz)
            min_num.SetName(out)
            min_num.Bind(wx.EVT_SPINCTRL, OnMinChange)

            max_num = wx.SpinCtrl(panel, wx.ID_ANY, min=0,max=127,
                initial=127, value="127", style=spin_style, size=range_sz)
            max_num.SetName(out)
            max_num.Bind(wx.EVT_SPINCTRL, OnMaxChange)

            flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL
            flag = flag | wx.BOTTOM if i == 1 else flag
            border = 30 if i == 1 else 0
            axis_box.Add(label, wx.GBPosition(y,0),flag=flag,border=border)
            axis_box.Add(dropdown, wx.GBPosition(y,1),flag=flag,border=border)
            axis_box.Add(min_num, wx.GBPosition(y,3),flag=flag,border=border)
            axis_box.Add(max_num, wx.GBPosition(y,4),flag=flag,border=border)

            controls = [dropdown,min_num,max_num]

            self.control_dict[key] = controls

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
                    initial=0, value="0", style=spin_style, size=range_sz)
                ctrl_num.SetName(out)
                ctrl_num.Bind(wx.EVT_SPINCTRL, OnControllerChange)
                self.control_dict[key].append(ctrl_num)
                axis_box.Add(ctrl_num, wx.GBPosition(y,2), flag=flag)

        box.Add(axis_box, flag=wx.ALL, border=20)
        box.Add(footer, border=20, flag=wx.ALL)


        panel.SetSizer(box)
        panel.Layout()

        # for k,v in self.control_dict.iteritems():
        #     print len(v)

        self.UpdateAllRowVals()

        # ACTUALLY START APP
        self.music_app.start()

    def UpdateAllRowVals(self): # WARNING: EXTREME HAX AHEAD
        set_vals = ["note","velocity","controller1","controller2","controller3","controller4"]
        for v in set_vals:
            global_val = globals()[v]
            global_range = globals()["range_"+v] # worst code i have ever written in my life :'( loljk hax
            global_port = None
            if "controller" in v:
                global_port = globals()["ctrlPort" + v[-1]] # just kidding. THIS is the worst. srsly.
            self.UpdateRowValues(v,global_val,global_range[0],global_range[1],global_port)

            # ^ Dear sweet baby Jesus this worked on the first try.
            # i [love|hate] Python
            # brb retiring from CS forever

    def UpdateRowValues(self,key,axis,min,max,port=None):
        if key in self.control_dict.keys():
            controls = self.control_dict[key]
            combo = controls[0]
            min_spin = controls[1]
            max_spin = controls[2]

            i = 0
            for option in combo.GetItems():
                if option.lower() == axis:
                    combo.Select(i)
                    break
                else:
                    i += 1

            min_spin.SetValue(min)
            max_spin.SetValue(max)

            if port is not None and len(controls) > 3:
                port_ctrl = controls[3]
                port_ctrl.SetValue(port)

    def GenDefaultLabel(self,window,text):
        label_text = wx.StaticText(window, wx.ID_ANY, text)
        label_text.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
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
        i = arg.GetInt()
        self.music_app.set_out(i)

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
top.SetSizeWH(650,450)
top.Show()
app.MainLoop()