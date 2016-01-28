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
    import Tkinter as tk
except:
    import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import time

__author__ = "Brian Perrett"


class Rigolx:

    checkqueuedelay = 40 # milliseconds
    addqueuetime = .1 # seconds

    def __init__(self, rigol, q1, q2):
        self.dev = rigol
        self.q1 = q1
        self.q2 = q2

    def start(self):
        """
        """
        self.root = tk.Tk()
        self.root.after(self.checkqueuedelay, self.checkQueue1Poll, self.q1)
        self.root.after(self.checkqueuedelay, self.checkQueue2Poll, self.q2)
        self.root.title("Rigol DS1000D/E Interface")
        self.makeWaveformFrame()
        self.ch1 = False
        self.ch2 = False
        self.root.mainloop()

    def checkQueue1Poll(self, c_queue):
        try:
            data = c_queue.get(0)
            self.p.set_ydata(data)
            if self.ch1:
                self.canvas.show()
        except Empty:
            pass
        finally:
            self.root.after(self.checkqueuedelay, self.checkQueue1Poll, c_queue)

    def checkQueue2Poll(self, c_queue):
        try:
            data = c_queue.get(0)
            self.p2.set_ydata(data)
            if self.ch2:
                self.canvas.show()
        except Empty:
            pass
        finally:
            self.root.after(self.checkqueuedelay, self.checkQueue2Poll, c_queue)

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
        if self.ch1:
            self.ch1 = False
            self.dev.channelDisplay(1, on=False)
        else:
            self.ch1 = True
            self.dev.channelDisplay(1, on=True)

    def showChannel2(self):
        if self.ch2:
            self.ch2 = False
            self.dev.channelDisplay(2, on=False)
        else:
            self.ch2 = True
            self.dev.channelDisplay(2, on=True)


def getWaveformData(q1, q2, dev, rigol):
    """
    dev - device connection
    rigol - rigolx class instance
    """
    while rigol.ch1 or rigol.ch2:
        print("Retrieving Data")
        x = dev.getTimebase()
        if rigol.ch1:
            y1 = dev.getWaveform("CHAN1")
            q1.put([x, y1])
        if rigol.ch2:
            y2 = dev.getWaveform("CHAN2")
            q2.put([x, y2])
        time.sleep(Rigolx.addqueuetime)


def main():
    q1 = Queue()
    q1.cancel_join_thread()
    q2 = Queue()
    q2.cancel_join_thread()
    dev = rigol.Rigol("usbtmc")

    r = Rigolx(dev, q1, q2)
    t1 = Process(target=getWaveformData, args=(q1, q2, dev, r))
    t1.start()
    # t2 = Process(target=getWaveformData2, args=(q2, dev, r))
    r.start()

    t1.join()
    # t2.join()
    t1.exit.set()
    # t2.exit.set()


if __name__ == '__main__':
    main()
