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

    def __init__(self, rigol_backend="usbtmc", checkqueuedelay=.04, addqueuetime=.1):
        """
        checkqueuedelay -> How quickly python will check the queues for new voltage
            data to plot.  This value must be less than addqueuetime to ensure that
            every waveform is being plotted.
        addqueuetime -> python waits <addqueuetime> seconds between each query about
            the voltages from the oscilloscope.
        q1 and q2 are the the queues which hold the voltage data for channel 1 and 2
            on the oscilloscope.
        """
        self.checkqueuedelay = checkqueuedelay * 1000  # in ms
        self.addqueuetime = addqueuetime  # in sec
        self.dev = rigol.Rigol(rigol_backend)
        self.q1 = Queue()
        self.q1.cancel_join_thread()
        self.q2 = Queue()
        self.q2.cancel_join_thread()
        self.ch1 = False
        self.ch2 = False

    def start(self):
        """
        Render the GUI.  Start checking the voltage queues
        """
        self.root = tk.Tk()
        self.root.after(self.checkqueuedelay, self.checkQueue1, self.q1)
        self.root.after(self.checkqueuedelay, self.checkQueue2, self.q2)
        self.root.title("Rigol DS1000D/E Interface")
        self.makeWaveformFrame()
        self.root.mainloop()

    def checkQueue1(self, q):
        if self.ch1:
            try:
                data = q.get(0)
                self.p.set_ydata(data)
                if self.ch1:
                    self.canvas.show()
            except Empty:
                pass
            finally:
                self.root.after(self.checkqueuedelay, self.checkQueue1, q)
        else:
            time.sleep(self.addqueuetime)

    def checkQueue2(self, q):
        if self.ch2:
            try:
                data = q.get(0)
                self.p2.set_ydata(data)
                if self.ch2:
                    self.canvas.show()
            except Empty:
                pass
            finally:
                self.root.after(self.checkqueuedelay, self.checkQueue2, q)
        else:
            time.sleep(self.addqueuetime)

    def makeWaveformFrame(self):
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
        self.p, = self.wave.plot([1, 2, 3], [5, 5, 5])
        self.p2, = self.wave.plot([1, 2, 3], [4, 4, 4])
        self.wave.set_xlabel("Time (seconds)")
        self.wave.set_ylabel("Voltage, (V)")
        self.canvas.show()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.wf_full)
        self.toolbar.pack()
        self.toolbar.update()

        # Buttons
        self.ch1_button = tk.Button(self.wf_button_frame, text="CH1", command=self.showChannel1)
        self.ch2_button = tk.Button(self.wf_button_frame, text="CH2", command=self.showChannel2)
        self.ch1_button.grid(row=0, column=0, padx=140, pady=5, ipadx=10, ipady=10)
        self.ch2_button.grid(row=0, column=1, padx=140, pady=5, ipadx=10, ipady=10)
        self.wf_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def showChannel1(self):
        """
        start process if neither were on before.
        If this function causes both channels to be off, terminate the
            processes.
        """
        if not self.ch1 and not self.ch2:
            self.t1 = Process(target=self.getWaveformData, args=())
        if self.ch1:
            self.ch1 = False
        else:
            self.ch1 = True
        if not self.ch1 and not self.ch2:
            self.t1.join()
            self.t1.terminate()

    def showChannel2(self):
        """
        start process if neither were on before.
        If this function causes both channels to be off, terminate the
            processes.
        """
        if not self.ch1 and not self.ch2:
            self.t1 = Process(target=self.getWaveformData, args=())
        if self.ch2:
            self.ch2 = False
        else:
            self.ch2 = True
        if not self.ch1 and not self.ch2:
            self.t1.join()
            self.t1.terminate()

    def getWaveformData(self):
        """
        dev - device connection
        rigol - rigolx class instance
        """
        while True:
            x = self.dev.getTimebase()
            if self.ch1:
                y1 = self.dev.getWaveform("CHAN1")
                self.q1.put([x, y1])
            if self.ch2:
                y2 = self.dev.getWaveform("CHAN2")
                self.q2.put([x, y2])
            time.sleep(self.addqueuetime)


def main():
    r = rigolx()


if __name__ == '__main__':
    main()
