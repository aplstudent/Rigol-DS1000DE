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
from multiprocessing import Process, Queue
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

    def __init__(self, rigol_backend="usbtmc", checkqueuedelay=.03, addqueuetime=.07):
        """
        checkqueuedelay -> How quickly python will check the queues for new voltage
            data to plot.  This value must be less than addqueuetime to ensure that
            every waveform is being plotted.
        addqueuetime -> python waits <addqueuetime> seconds between each query about
            the voltages from the oscilloscope.
        q1 and q2 are the the queues which hold the voltage data for channel 1 and 2
            on the oscilloscope.
        """
        self.checkqueuedelay = int(checkqueuedelay * 1000)  # in ms
        self.addqueuetime = addqueuetime  # in sec
        self.dev = rigol.Rigol(rigol_backend)
        self.dev.waveformPointsMode("NORM")
        self.vpp = self.dev.askChannelScale(1) * 4
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
        # self.root.after(self.checkqueuedelay, self.checkQueue2, q2)
        self.root.title("Rigol DS1000D/E Interface")
        self.makeWaveformFrame(q1, q2)
        print("STARTING PROCESS 1")
        self.t1 = Process(target=self.getWaveformData, args=(q1, q2))
        self.t1.start()
        self.root.mainloop()

    def checkQueue1(self, q1, q2):
        try:
            data1 = q1.get(0)
            data2 = q2.get(0)
            # print(data)
            # print(dir(self.wave))
            if self.ch1:
                self.p.set_xdata(self.x)
                self.p.set_ydata(data1)
            if self.ch2:
                self.p2.set_xdata(self.x)
                self.p2.set_ydata(data2)
            self.wf.canvas.draw()
        except Empty:
            pass
        finally:
            self.root.after(self.checkqueuedelay, self.checkQueue1, q1, q2)

    def makeWaveformFrame(self, q1, q2):
        """
        Add the waveform frame to self.root
        https://sukhbinder.wordpress.com/2014/06/10/matplotlib-embedded-with-tkinter/
        """
        self.wf_full = tk.Frame(self.root)
        self.wf_button_frame = tk.Frame(self.wf_full)
        self.wf = Figure(figsize=(7, 5), dpi=80)
        self.wf_full.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.canvas = FigureCanvasTkAgg(self.wf, master=self.wf_full)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.wave = self.wf.add_axes([0.09, 0.13, .85, .8], frameon=True)
        self.p, = self.wave.plot([], [], linewidth=2.5)
        self.p2, = self.wave.plot([], [], linewidth=2.5)
        self.wave.legend(["Channel 1", "Channel 2"])
        # print(dir(self.p))
        self.wave.set_xlabel("Time (seconds)")
        self.wave.set_ylabel("Voltage, (V)")
        self.wave.set_ylim(-self.vpp, self.vpp)
        self.wave.set_xlim(self.x[0],self.x[-1])
        self.canvas.show()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.wf_full)
        self.toolbar.pack()
        self.toolbar.update()

        # Buttons
        self.ch1_button = tk.Button(self.wf_button_frame, text="CH1", command=lambda: self.showChannel(1))
        self.ch2_button = tk.Button(self.wf_button_frame, text="CH2", command=lambda: self.showChannel(2))
        self.ch1_button.grid(row=0, column=0, padx=140, pady=5, ipadx=10, ipady=10)
        self.ch2_button.grid(row=0, column=1, padx=140, pady=5, ipadx=10, ipady=10)
        self.wf_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def showChannel(self, channel):
        """
        start process if neither were on before.
        If this function causes both channels to be off, terminate the
            processes.
        """            
        if channel==1 and self.ch1:
            x = self.dev.channelDisplay(1, False)
            self.ch1 = False
            self.p.set_xdata([])
            self.p.set_ydata([])
        elif channel==1 and not self.ch1:
            x = self.dev.channelDisplay(1, True)
            self.ch1 = True
        if channel==2 and self.ch2:
            x = self.dev.channelDisplay(2, False)
            self.ch2 = False
            self.p2.set_xdata([])
            self.p2.set_ydata([])
        elif channel==2 and not self.ch2:
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
