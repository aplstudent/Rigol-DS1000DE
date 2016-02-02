"""
Advanced Physics Lab - University of Oregon
Jan 26th, 2016
A user interface for controlling the Rigol DS1000D/E oscilloscopes

Source for integrating matplotlib plots to tkinter
    - http://matplotlib.org/examples/user_interfaces/embedding_in_tk.html
multiprocessing based off of the answer to this post
    - http://stackoverflow.com/questions/13228763/using-multiprocessing-module-for-updating-tkinter-gui
"""
from __future__ import division
from multiprocessing import Process, Queue, RLock
from Queue import Empty
import rigol
try:
    import Tkinter as tk  # python2
except:
    import tkinter as tk  # python3
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import time

__author__ = "Brian Perrett"


class Rigolx:

    def __init__(self, rigol_backend="usbtmc", checkqueuedelay=.09, addqueuetime=.2):
        """
        checkqueuedelay -> How quickly python will check the queues for new voltage
            data to plot.  This value must be less than addqueuetime to ensure that
            every waveform is being plotted.
        addqueuetime -> python waits <addqueuetime> seconds between each query about
            the voltages from the oscilloscope.
        q1 and q2 are the the queues which hold the voltage data for channel 1 and 2
            on the oscilloscope.
        """
        self.lock = RLock()
        self.checkqueuedelay = int(checkqueuedelay * 1000)  # in ms
        self.addqueuetime = addqueuetime  # in sec
        self.dev = rigol.Rigol(rigol_backend)
        self.dev.waveformPointsMode("NORM")
        self.vpp = self.dev.askChannelScale(1) * 4
        self.vpp2 = self.dev.askChannelScale(2) * 4
        self.x = self.dev.getTimebase()
        q1 = Queue()
        q1.cancel_join_thread()
        q2 = Queue()
        q2.cancel_join_thread()
        self.ch1 = False
        self.ch2 = False
        self.start(q1, q2)

    def start(self, q1, q2):
        """
        Render the GUI.  Start checking the voltage queues
        """
        self.root = tk.Tk()
        self.root.after(self.checkqueuedelay, self.checkQueue1, q1, q2)
        self.root.title("Rigol DS1000D/E Interface")
        self.makeWaveformFrame(q1, q2)
        self.makeScalingFrame()
        self.makeInfoPanel()
        print("STARTING PROCESS 1")
        self.t1 = Process(target=self.getWaveformData, args=(q1, q2))
        self.t1.start()
        self.root.mainloop()

    def refresh(self):
        """
        """
        vpp1 = self.dev.measureVpp(1)
        vpp2 = self.dev.measureVpp(2)
        self.channel1vppentry.config(state="normal")
        self.channel1vppentry.delete(0, "end")
        self.channel1vppentry.insert("end", vpp1)
        self.channel1vppentry.config(state="readonly")
        self.channel2vppentry.config(state="normal")
        self.channel2vppentry.delete(0, "end")
        self.channel2vppentry.insert("end", vpp2)
        self.channel2vppentry.config(state="readonly")

    def setVoltsPerDiv(self, Event=None):
        """
        """
        vperdiv = self.vperdiventry.get()
        self.dev.channelScale(1, vperdiv)
        time.sleep(.1)
        self.vpp = self.dev.askChannelScale(1) * 4
        self.wave.set_ylim(-self.vpp, self.vpp)

    def setVoltsPerDiv2(self, Event=None):
        """
        """
        vperdiv = self.vperdiventry2.get()
        self.dev.channelScale(2, vperdiv)
        time.sleep(.1)
        self.vpp2 = self.dev.askChannelScale(2) * 4
        self.wave2.set_ylim(-self.vpp2, self.vpp2)

    def setSecPerDiv(self, Event=None):
        spd = self.timescaleentry.get()
        self.dev.timebaseScale(spd)
        time.sleep(.1)
        self.x = self.dev.getTimebase()
        self.wave.set_xlim(self.x[0], self.x[-1])
        self.wave2.set_xlim(self.x[0], self.x[-1])

    def checkQueue1(self, q1, q2):
        """
        Notice there are 2 release statements in this method.  It is because
            sometimes the method will not make it to the first release because of
            the queues being empty, so I've written a second release method to
            ensure that the lock is released
        """
        try:
            data1 = q1.get(0)
            data2 = q2.get(0)
            # print(data)
            # print(dir(self.wave))
            if self.ch1:
                # print(len(self.x))
                # print(len(data1))
                self.p.set_xdata(self.x[:len(data1)])
                self.p.set_ydata(data1)
            if self.ch2:
                self.p2.set_xdata(self.x[:len(data2)])
                self.p2.set_ydata(data2)
        except Empty:
            pass
        finally:
            if self.ch1 or self.ch2:
                self.wf.canvas.draw()
            self.root.after(self.checkqueuedelay, self.checkQueue1, q1, q2)

    def makeWaveformFrame(self, q1, q2):
        """
        Add the waveform frame to self.root
        https://sukhbinder.wordpress.com/2014/06/10/matplotlib-embedded-with-tkinter/
        """
        self.wf_full = tk.Frame(self.root)
        self.wf_button_frame = tk.Frame(self.wf_full)
        self.wf = Figure(figsize=(11, 9), dpi=80, linewidth=1, frameon=False)
        # self.wf_full.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.wf_full.grid(row=0, column=0)
        self.canvas = FigureCanvasTkAgg(self.wf, master=self.wf_full)
        # self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)
        self.wave2 = self.wf.add_axes([0.09, 0.13, .85, .4], frameon=True)
        self.wave = self.wf.add_axes([0.09, 0.55, .85, .4], frameon=True)
        #  change the color of borders, labels, ticks, title
        self.wave.axes.xaxis.set_ticklabels([])
        self.wave.spines["bottom"].set_color("#cccccc")
        self.wave.spines["right"].set_color("#cccccc")
        self.wave.spines["top"].set_color("#cccccc")
        self.wave.spines["left"].set_color("#cccccc")
        self.wave.tick_params(axis='x', colors='#8c8c8c')
        self.wave.tick_params(axis='y', colors='#8c8c8c')
        self.wave.yaxis.label.set_color('#8c8c8c')
        self.wave.xaxis.label.set_color('#8c8c8c')
        self.wave.title.set_color('#8c8c8c')
        self.wave.grid()

        self.wave2.spines["bottom"].set_color("#cccccc")
        self.wave2.spines["right"].set_color("#cccccc")
        self.wave2.spines["top"].set_color("#cccccc")
        self.wave2.spines["left"].set_color("#cccccc")
        self.wave2.tick_params(axis='x', colors='#8c8c8c')
        self.wave2.tick_params(axis='y', colors='#8c8c8c')
        self.wave2.yaxis.label.set_color('#8c8c8c')
        self.wave2.xaxis.label.set_color('#8c8c8c')
        self.wave2.title.set_color('#8c8c8c')
        self.wave2.grid()

        self.p, = self.wave.plot([], [], linewidth=2, color="#007acc", label="Channel 1")
        self.p2, = self.wave2.plot([], [], linewidth=2, color="#ff4d4d", label="Channel 2")
        # self.wave.legend(["Channel 1", "Channel 2"])
        # print(dir(self.p))

        # self.wave.set_xlabel("Time (seconds)")
        self.wave.set_ylabel("Voltage, (V)")
        self.wave.set_ylim(-self.vpp, self.vpp)
        self.wave.set_xlim(self.x[0],self.x[-1])

        self.wave2.set_xlabel("Time (seconds)")
        self.wave2.set_ylabel("Voltage, (V)")
        self.wave2.set_ylim(-self.vpp2, self.vpp2)
        self.wave2.set_xlim(self.x[0],self.x[-1])

        self.canvas.show()
        self.toolbar_frame = tk.Frame()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.pack()
        self.toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="W")
        self.toolbar.update()

        # Buttons
        self.ch1_button = tk.Button(self.wf_button_frame, text="CH1", command=lambda: self.showChannel(1))
        self.ch2_button = tk.Button(self.wf_button_frame, text="CH2", command=lambda: self.showChannel(2))
        self.ch1_button.grid(row=0, column=0, ipadx=10, ipady=10, padx=(0, 40))
        self.ch2_button.grid(row=0, column=1, ipadx=10, ipady=10, padx=(40, 0))
        # self.wf_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.wf_button_frame.grid(row=2, column=0)

        # Allow resizing.  Omitting this portion will keep every frame the
        #    same size despite window resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.wf_full.columnconfigure(0, weight=1)
        self.wf_full.rowconfigure(0, weight=1)
        self.toolbar_frame.columnconfigure(0, weight=1)
        self.toolbar_frame.rowconfigure(0, weight=1)
        self.wf_button_frame.columnconfigure(0, weight=1)
        self.wf_button_frame.rowconfigure(0, weight=1)
        self.toolbar.columnconfigure(0, weight=1)
        self.toolbar.rowconfigure(0, weight=1)

    def makeScalingFrame(self):
        """
        """
        self.scale_frame = tk.Frame(self.root)

        # General Settings
        self.generalsettingslabel = tk.Label(self.scale_frame, text="General Settings")
        self.timescaleentry = tk.Entry(self.scale_frame)
        self.timescalebutton = tk.Button(self.scale_frame, text="SET S/DIV", command=self.setSecPerDiv)

        # Volts/Div channel 1
        self.channel1label = tk.Label(self.scale_frame, text="Channel 1 Settings")
        self.vperdiventry = tk.Entry(self.scale_frame)
        self.vperdivbutton = tk.Button(self.scale_frame, text="SET V/DIV", command=self.setVoltsPerDiv)

        # Volts/Div channel 2
        self.channel2label = tk.Label(self.scale_frame, text="Channel 2 Settings")
        self.vperdiventry2 = tk.Entry(self.scale_frame)
        self.vperdivbutton2 = tk.Button(self.scale_frame, text="SET V/DIV", command=self.setVoltsPerDiv2)

        # Layout
        row = 0
        self.generalsettingslabel.grid(row=row, column=0, columnspan=2)

        row += 1
        self.timescaleentry.grid(row=row, column=0)
        self.timescalebutton.grid(row=row, column=1)

        row += 1
        self.channel1label.grid(row=row, column=0, columnspan=2, pady=(20, 0))

        row += 1
        self.vperdiventry.grid(row=row, column=0, padx=5, pady=5)
        self.vperdivbutton.grid(row=row, column=1, padx=(0, 5), pady=5)

        row += 1
        self.channel2label.grid(row=row, column=0, columnspan=2, pady=(20, 0))

        row += 1
        self.vperdiventry2.grid(row=row, column=0, padx=5, pady=5)
        self.vperdivbutton2.grid(row=row, column=1, padx=(0, 5), pady=5)

        self.scale_frame.grid(row=0, column=1, sticky="N")
        
        self.vperdiventry.bind("<Return>", self.setVoltsPerDiv)
        self.timescaleentry.bind("<Return>", self.setSecPerDiv)
        self.vperdiventry2.bind("<Return>", self.setVoltsPerDiv2)

    def makeInfoPanel(self):
        """
        """
        color = "#ccffcc"

        self.infoframe = tk.Frame(self.root, borderwidth=2, bg=color, relief="groove")

        self.channel1infolabel = tk.Label(self.infoframe, text="Channel 1 Info", bg=color)
        self.channel2infolabel = tk.Label(self.infoframe, text="Channel 2 Info", bg=color)
        self.channel1vppentry = tk.Entry(self.infoframe)
        self.channel1vpplabel = tk.Label(self.infoframe, text="VPP", bg=color)
        self.channel2vppentry = tk.Entry(self.infoframe)
        self.channel2vpplabel = tk.Label(self.infoframe, text="VPP", bg=color)

        self.inforefreshbutton = tk.Button(self.infoframe, text="Refresh", command=self.refresh)

        #  Layout
        row = 0
        self.channel1infolabel.grid(row=row, column=0, columnspan=2)

        row += 1
        self.channel1vppentry.grid(row=row, column=0)
        self.channel1vpplabel.grid(row=row, column=1)

        row += 1
        self.channel2infolabel.grid(row=row, column=0, columnspan=2)

        row += 1
        self.channel2vppentry.grid(row=row, column=0)
        self.channel2vpplabel.grid(row=row, column=1)

        row += 1
        self.inforefreshbutton.grid(row=row, column=1)

        self.infoframe.grid(row=0, column=2, rowspan=2, sticky="N")

        vpp1 = self.dev.measureVpp(1)
        vpp2 = self.dev.measureVpp(2)
        self.channel1vppentry.insert("end", vpp1)
        self.channel1vppentry.config(state="readonly")
        self.channel2vppentry.insert("end", vpp2)
        self.channel2vppentry.config(state="readonly")

        # Volts/Div channel 2     

    def showChannel(self, channel):
        """
        start process if neither were on before.
        If this function causes both channels to be off, terminate the
            processes.
        """
        if channel == 1 and self.ch1:
            x = self.dev.channelDisplay(1, False)
            self.ch1 = False
            self.p.set_xdata([])
            self.p.set_ydata([])
        elif channel == 1 and not self.ch1:
            x = self.dev.channelDisplay(1, True)
            self.ch1 = True
        if channel == 2 and self.ch2:
            x = self.dev.channelDisplay(2, False)
            self.ch2 = False
            self.p2.set_xdata([])
            self.p2.set_ydata([])
        elif channel == 2 and not self.ch2:
            x = self.dev.channelDisplay(2, True)
            self.ch2 = True
        self.wf.canvas.draw()
        # if not self.ch1 and not self.ch2:
            # self.t1.join()
            # self.t1.terminate()

    def getWaveformData(self, q1, q2):
        """
        dev - device connection
        rigol - rigolx class instance
        """
        while True:
            # start_time = time.time()
            y1 = self.dev.getWaveform("CHAN1")
            q1.put(y1)
            y2 = self.dev.getWaveform("CHAN2")
            q2.put(y2)
            time.sleep(self.addqueuetime)
            # print(time.time() - start_time)


def main():
    r = Rigolx()
    r.t1.terminate()

if __name__ == '__main__':
    main()
