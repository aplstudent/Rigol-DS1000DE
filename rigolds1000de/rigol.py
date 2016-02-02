# -*- coding: utf-8 -*-
"""
rigol.py
University of Oregon - Advanced Physics Lab
Built on top of rigolSkeleton.py to control the rigol ds 1000d/e
    series oscilloscopes

Using this programming guide -> http://www.batronix.com/pdf/Rigol/ProgrammingGuide/DS1000DE_ProgrammingGuide_EN.pdf
sources I used
- http://scruss.com/blog/tag/usbtmc/
- http://www.righto.com/2013/07/rigol-oscilloscope-hacks-with-python.html
- http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
"""
from __future__ import division
import usbcon as uc
import numpy as np
import ast
try:
    import tkFileDialog as tkfd  # python2
except:
    import tkinter.filedialog as tkfd  # python3

__author__ = "Brian Perrett"


class InvalidBackendException(Exception):
    pass


class InvalidArgument(Exception):
    pass


class Rigol:

    backends = ["usbtmc"]

    def __init__(self, backend, idProduct=None, idVendor=None):
        """
        The volt1/2_scale attributes, along with other attributes defined here
            should always be up to date if you are changing them solely with the methods
            of this class.  If you change the voltage scale on the oscilloscope manually,
            you have to update these attributes manually also, or just use the "ask" methods
            to query the volt scale/offset or time scale/offset.
        """
        if backend == "usbtmc":
            self.dev = uc.UsbCon(idProduct=idProduct, idVendor=idVendor)
        else:
            raise InvalidBackendException("Please specify a valid backend such as {}".format(self.backends))
        delay = True if self.askTimebaseMode() == "DEL" else False
        self.volt1_scale = self.askChannelScale(1)
        self.volt1_offset = self.askChannelOffset(1)
        self.volt2_scale = self.askChannelScale(2)
        self.volt2_offset = self.askChannelOffset(2)
        self.time_scale = self.askTimebaseScale(delayed=delay)
        self.time_offset = self.askTimebaseOffset(delayed=delay)

    def identify(self):
        return self.dev.ask("*IDN?")

    def reset(self):
        self.dev.write("*RST")

    def run(self):
        self.dev.write(":RUN")

    def stop(self):
        """
        Stops data acquisition
        """
        self.dev.write(":STOP")

    def hardcopy(self):
        """
        Apparently saves a bitmap of the screen somewhere, but I have no idea where.
        """
        self.dev.write(":HARDcopy")

    def auto(self):
        self.dev.write(":AUTO")

    def refreshAttributes(self):
        """
        In case settings are changed manually on the oscilloscope, we can reset all
            of our class attributes with this method.
        """
        delay = True if self.askTimebaseMode() == "DEL" else False
        self.volt1_scale = self.askChannelScale(1)
        self.volt1_offset = self.askChannelOffset(1)
        self.volt2_scale = self.askChannelScale(2)
        self.volt2_offset = self.askChannelOffset(2)
        self.time_scale = self.askTimebaseScale(delayed=delay)
        self.time_offset = self.askTimebaseOffset(delayed=delay)

    ###########
    # ACQUIRE #
    ###########
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    """

    # ACQUIRE 1
    def acquireType(self, typ):
        """
        The commands set the current acquire type of the oscilloscope.
        <type> could be NORM, AVER or PEAK.
        """
        valid = ["NORM", "AVER", "PEAK"]
        if typ not in valid:
            raise InvalidArgument("Typ(e) argument must be one of {}.".format(valid))
        msg = ":ACQ:TYPE {}".format(typ)
        self.dev.write(msg)

    def askAcquireType(self):
        """
        Query acquire type of oscilloscope.
        The query returns NORMAL, AVERAGE or PEAKDETECT
        """
        msg = ":ACQ:TYPE?"
        return self.dev.ask(msg)

    # ACQUIRE 2
    def acquireMode(self, mode):
        """
        The commands set the current acquire mode of the oscilloscope.
        <mode> could be RTIM (Real time Sampling) or ETIM (Equivalent Sampling).
        """
        valid = ["RTIM", "ETIM"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid))
        msg = ":ACQ:MODE {}".format(mode)
        self.dev.write(msg)

    def askAcquireMode(self):
        """
        Query acquire mode for oscilloscope.
        The query returns REAL_TIME or EQUAL_TIME.
        """
        msg = ":ACQ:MODE?"
        return self.dev.ask(msg)

    # ACQUIRE 3
    def acquireAverages(self, count):
        """
        The commands set the average numbers in Average mode. <count>
        could be and integer of 2 times the power of N within 2 and 256.
        """
        valid = [2, 4, 8, 16, 32, 64, 128, 256]
        if count not in valid:
            raise InvalidArgument("Count argument must be one of {}.".format(valid))
        msg = ":ACQ:AVER {}".format(count)
        self.dev.write(msg)

    def askAcquireAverages(self):
        """
        The query returns 2, 4, 8, 16, 32, 64, 128 or 256.
        """
        msg = ":ACQ:AVER?"
        return self.dev.ask(msg)

    # ACQUIRE 4
    def askAcquireSamplingRate(self, channel):
        """
        The command queries the current sampling rate of the analog channel or digital
        channel (only for DS1000D series).
        """
        valid = [1, 2]
        if channel not in valid:
            raise InvalidArgument("Channel argument must be one of {}.".format(channel))
        msg = ":ACQ:SAMP? CHAN{}".format(channel)
        return self.dev.ask(msg)

    # ACQUIRE 5
    def acquireMemDepth(self, depth):
        """
        The commands set and query the memory depth of the oscilloscope. <depth>
        could be LONG (long memory) or NORMal (normal memory)
        """
        valid = ["LONG", "NORM"]
        if depth not in valid:
            raise InvalidArgument("Depth argument must be one of {}.".format(valid))
        msg = ":ACQ:MEMD {}".format(depth)
        self.dev.write(msg)

    def askAcquireMemDepth(self):
        """
        The query returns LONG or NORMAL.
        """
        msg = ":ACQ:MEMD?"
        return self.dev.ask(msg)

    ###########
    # DISPLAY #
    ###########
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    6 - yes
    7 - yes
    8 - yes
    """
    # DISPLAY 1
    def displayType(self, typ):
        """
        The commands set the display type between sampling points. <type>
        could be VECT (vector display) or DOTS (point display).
        """
        valid = ["VECT", "DOTS"]
        if typ not in valid:
            raise InvalidArgument("Typ(e) argument must be one of {}.".format(valid))
        msg = ":DISP:TYPE {}".format(typ)
        self.dev.write(msg)

    def askDisplayType(self):
        """
        The query returns VECTORS or DOTS.
        """
        msg = ":DISP:TYPE?"
        return self.dev.ask(msg)

    # DISPLAY 2
    def displayGrid(self, grid):
        """
        The commands set and query the state of the screen grid. <grid> could be FULL
        (open the background grid and coordinates), HALF (turn off the background grid)
        or NONE (turn off the background grid and coordinates).
        """
        valid = ["FULL", "HALF", "NONE"]
        if grid not in valid:
            raise InvalidArgument("Grid argument must be one of {}.".format(valid))
        msg = ":DISP:GRID {}".format(grid)
        self.dev.write(msg)

    def askDisplayGrid(self):
        """
        The query returns FULL, HALF or NONE.
        """
        msg = ":DISP:GRID?"
        return self.dev.ask(msg)

    # DISPLAY 3
    def displayPersist(self, persist=True):
        """
        The commands set and query the state of the waveform persist. “ON” denotes
        the record points hold until disable the presist, “OFF” denotes the record point
        varies in high refresh rate.
        persist can take on boolean values True or False.
        """
        msg = ":DISP:PERS {}".format("ON" if persist else "OFF")
        self.dev.write(msg)

    def askDisplayPersist(self):
        """
        The query returns ON or OFF.
        """
        msg = ":DISP:PERS?"
        return self.dev.ask(msg)

    # DISPLAY 4
    def displayMnuDisplay(self, t):
        """
        The commands set and query the time for hiding menus automatically. <time>
        could be 1s, 2s, 5s, 10s, 20s or Infinite.
        """
        valid = ["1", "2", "5", "10", "20", "Infinite"]
        if str(t) not in valid:
            raise InvalidArgument("t(ime) argument must be one of {}.".format(valid))
        msg = ":DISP:MNUD {}".format(t)
        self.dev.write(msg)

    def askDisplayMnuDisplay(self):
        """
        The query returns 1s, 2s, 5s, 10s, 20s or Infinite.
        """
        msg = ":DISP:MNUD?"
        return self.dev.ask(msg)

    # DISPLAY 5
    def displayMnuStatus(self, disp=True):
        """
        The commands set and query the state of the operation menu.
        disp can take boolean values True or False, to either display
            menu status or not.
        """
        msg = ":DISP:MNUS {}".format("ON" if disp else "OFF")
        self.dev.write(msg)

    def askDisplayMnuStatus(self):
        """
        The query returns ON or OFF.
        """
        msg = ":DISP:MNUS?"
        return self.dev.ask(msg)

    # DISPLAY 6
    def displayClear(self):
        """
        The command clears out of date waveforms on the screen during waveform
        persist.
        """
        msg = ":DISP:CLE"
        self.dev.write(msg)

    # DISPLAY 7
    def displayBrightness(self, level):
        """
        Changes the brightness level of the grid.
        level - Brightness level from 0 to 32
        """
        if level not in range(33):
            raise InvalidArgument("Level argument must be between 0 and 32.")
        self.dev.write(":DISP:BRIG {}".format(level))

    def askDisplayBrightness(self):
        """
        query the brightness of the grid
        returns a string from 0 to 32
        """
        return self.dev.ask(":DISP:BRIG?")

    # DISPLAY 8
    def displayIntensity(self, level):
        """
        level - intensity level from 0 to 32
        """
        if level < 0 or level > 32:
            raise InvalidArgument("level argument must be between 0 and 8.")
        self.dev.write(":DISP:INT {}".format(level))

    def askDisplayIntensity(self):
        """
        Returns waveform brightness from 0 to 32
        """
        return self.dev.ask(":DISP:INT?")

    ############
    # TIMEBASE #
    ############
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    """
    # TIMEBASE 1
    def timebaseMode(self, mode):
        """
        The commands set and query the scan mode of horizontal timebase. <mode>
        could be MAIN (main timebase) or DELayed (delayed scan).
        """
        valid = ["MAIN", "DEL"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid))
        msg = ":TIM:MODE {}".format(mode)
        self.dev.write(msg)

    def askTimebaseMode(self):
        """
        The query returns MAIN or DELAYED.
        """
        msg = ":TIM:MODE?"
        return self.dev.ask(msg)

    # TIMEBASE 2
    def timebaseOffset(self, offset, delayed=False):
        """
        The commands set and query the offset of the MAIN or DELayed timebase (that
        is offset of the waveform position relative to the trigger midpoint.). Thereinto,
        In NORMAL mode, the range of <scale_val> is 1s ~ end of the memory;
        In STOP mode, the range of <scale_val> is -500s ~ +500s;
        In SCAN mode, the range of <scale_val> is -6*Scale ~ +6*Scale; (Note: Scale
        indicates the current horizontal scale, the unit is s/div.)
        In MAIN state, the item [:DELayed] should be omitted.
        """
        # not checking for valid input.
        msg = ":TIM{}:OFFS {}".format(":DEL" if delayed else "", offset)
        self.dev.write(msg)
        self.time_offset = self.askTimebaseOffset(delayed=delayed)

    def askTimebaseOffset(self, delayed=False):
        """
        The query returns the setting value of the <offset> in s.
        """
        msg = ":TIM{}:OFFS?".format(":DEL" if delayed else "")
        offset = self.dev.ask(msg)
        self.time_offset = float(offset)
        return float(offset)

    # TIMEBASE 3
    def timebaseScale(self, scale, delayed=False):
        """
        The commands set and query the horizontal scale for MAIN or DELayed
        timebase, the unit is s/div (seconds/grid), thereinto:
        In YT mode, the range of <scale_val> is 2ns - 50s;
        In ROLL mode, the range of <scale_val> is 500ms - 50s;
        In MAIN state, the item [:DELayed] should be omitted.
        """
        msg = ":TIM{}:SCAL {}".format(":DEL" if delayed else "", scale)
        self.dev.write(msg)
        self.time_scale = self.askTimebaseScale(delayed=delayed)

    def askTimebaseScale(self, delayed=False):
        """
        The query returns the setting value of <scale_val> in s.
        """
        msg = ":TIM{}:SCAL?".format(":DEL" if delayed else "")
        scale = self.dev.ask(msg)
        self.time_scale = float(scale)
        return float(scale)

    def timebaseFormat(self, format):
        """
        The commands set and query the horizontal timebase. <value> could be XY, YT
        or SCANning.
        """
        valid = ["XY", "YT", "SCAN"]
        if format not in valid:
            raise InvalidArgument("Format argument must be one of {}".format(valid))
        msg = ":TIM:FORM {}".format(format)
        self.dev.write(msg)

    def askTimebaseFormat(self):
        """
        The query returns X-Y, Y-T or SCANNING.
        """
        msg = ":TIM:FORM?"
        return self.dev.ask(msg)

    """
    __TRIGGER FUNCTIONS__
    The trigger functions are separated into 8 sub-sections
    1. Trigger Control
    2. Edge Trigger
    3. Pulse Trigger
    4. Video Trigger
    5. Slope Trigger
    6. Pattern Trigger
    7. Duration Trigger
    8. Alternation Trigger
    """
    ######################
    # 1. TRIGGER CONTROL #
    ######################
    """
    Which trigger functions have been implemented.
    Numbering is based off of numbering in the programming manual.
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    6 - yes
    7 - yes
    8 - yes
    9 - yes
    """

    # TRIGGER CONTROL 1
    def triggerMode(self, mode):
        """
        sets trigger mode
        see valid_modes variable for valid mode values.
        """
        valid_modes = ["EDGE", "PULS", "VIDEO", "SLOP", "PATT", "DUR", "ALT"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}".format(valid_modes))
        self.dev.write(":TRIG:MODE {}".format(mode))

    def askTriggerMode(self):
        """
        queries trigger mode
        """
        return self.dev.ask(":TRIG:MODE?")

    # TRIGGER CONTROL 2
    def triggerSource(self, mode, source):
        """
        sets trigger mode and source
        """
        dig = ["DIG{}".format(x) for x in range(16)]
        if mode == "EDGE":
            valid_sources = ["CHAN1", "CHAN2", "EXT", "ACL"] + dig
        elif mode == "PULSE":
            valid_sources = ["CHAN1", "CHAN2", "EXT"] + dig
        elif mode == "VIDEO":
            valid_sources = ["CHAN1", "CHAN2", "EXT"]
        elif mode == "SLOP":
            valid_sources = ["CHAN1", "CHAN2", "EXT"]
        elif mode in ["PATTERN", "DURATION", "ALTERNATION"]:
            valid_sources = ["CHAN1", "CHAN2", "EXT", "ACL"] + dig
        else:
            raise InvalidArgument("Mode argument must be one of ".format(["EDGE", "PULS", "VIDEO", "SLOP", "PATT", "DUR", "ALT"]))
        if source not in valid_sources:
            raise InvalidArgument("Source argument must be one of {} for a trigger mode of {}".format(valid_sources, mode))
        else:
            msg = ":TRIG:{}:SOUR {}".format(mode, source)
            # print("Writing {}".format(msg))
            self.dev.write(msg)

    def askTriggerSource(self, mode):
        """
        query what trigger source is being used.
        mode - can be any of ["EDGE", "PULS", "VIDEO", "SLOP", "PATT", "DUR", "ALT"]
        """
        valid_modes = ["EDGE", "PULS", "VIDEO", "SLOP", "PATT", "DUR", "ALT"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        msg = ":TRIG:{}:SOUR?".format(mode)
        # print(msg)
        return self.dev.ask(msg)

    # TRIGGER CONTROL 3
    def triggerLevel(self, mode, level):
        """
        The commands set and query the trigger level. <mode> could be :EDGE, :PULSe
        or :VIDEO; the range of <level> is: -6*Scale~+6*Scale, Scale indicates the current vertical
        scale, the unit is V/div.
        """
        # We can check for valid inputs using the other methods.  Implement this later.
        valid_modes = ["EDGE", "PULS", "VIDEO"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        msg = ":TRIG{}:LEV {}".format(mode, level)
        self.dev.write(msg)

    def askTriggerLevel(self, mode):
        """
        The query returns the setting value of <level> in V.
        """
        valid_modes = ["EDGE", "PULS", "VIDEO"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        msg = ":TRIG{}:LEV?".format(mode)
        return self.dev.ask(msg)

    # TRIGGER CONTROL 4
    def triggerSweep(self, mode, sweep):
        """
        The commands set and query the trigger type. <mode>could be :EDGE,
        :PULSe, :SLOPe, :PATTern or :DURation.
        sweep can take values [AUTO, NORM, SING]
        """
        valid_modes = ["EDGE", "PULS", "SLOP", "PATT", "DUR"]
        valid_sweep = ["AUTO", "NORM", "SING"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        if sweep not in valid_sweep:
            raise InvalidArgument("Sweep argument must be one of {}.".format(valid_sweep))
        msg = ":TRIG:{}:SWE {}".format(mode, sweep)
        self.dev.write(msg)

    def askTriggerSweep(self, mode):
        """
        The query returns AUTO, NORMAL or SINGLE.
        """
        valid_modes = ["EDGE", "PULS", "SLOP", "PATT", "DUR"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        msg = ":TRIG:{}:SWE?".format(mode)
        return self.dev.ask(msg)

    # TRIGGER CONTROL 5
    def triggerCoupling(self, mode, coupling):
        """
        The commands set and query the coupling type. Thereinto,
        DC: Allow all signals pass.
        AC: Block DC signals and attenuate the signals lower than 10Hz.
        HF: Reject high frequency signals (Higher than 150KHz).
        LF: Reject DC signals and attenuate low frequency signals (Lower than 8KHz).
        <mode> could be :EDGE, :PULSe or :SLOPe.
        """
        valid_coupling = ["DC", "AC", "HF", "LF"]
        valid_modes = ["EDGE", "PULS", "SLOP"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        if coupling not in valid_coupling:
            raise InvalidArgument("Coupling argument must be one of {}.".format(valid_coupling))
        msg = ":TRIG:{}:COUP {}".format(mode, coupling)
        self.dev.write(msg)

    def askTriggerCoupling(self, mode):
        """
        The query returns DC, AC, HF or LF.
        """
        valid_modes = ["EDGE", "PULS", "SLOP"]
        if mode not in valid_modes:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid_modes))
        msg = ":TRIG:{}:COUP?".format(mode)
        return self.dev.ask(msg)

    # TRIGGER CONTROL 6
    def triggerHoldoff(self, count):
        """
        The commands set and query the trigger holfoff time. The range of <count> is
        <count>: 500ns~1.5s.
        """
        if count < .0000005 or count > 1.5:
            raise InvalidArgument("Count argument must be between 500ns and 1.5s")
        msg = ":TRIG:HOLD {}".format(count)
        self.dev.write(msg)

    def askTriggerHoldoff(self):
        """
        The query returns the setting value of <count> in s.
        """
        msg = ":TRIG:HOLD?"
        return self.dev.ask(msg)

    # TRIGGER CONTROL 7
    def askTriggerStatus(self):
        """
        The command queries the operating status of the oscilloscope. The status could
        be RUN, STOP, T`D, WAIT or AUTO.
        """
        msg = ":TRIG:STAT?"
        return self.dev.ask(msg)

    # TRIGGER CONTROL 8
    def trigger50(self):
        """
        The command sets the trigger level to the vertical midpoint of amplitude.
        """
        msg = ":TRIG%50"
        self.dev.write(msg)

    # TRIGGER CONTROL 9
    def triggerForce(self):
        """
        The command forces the oscilloscope to trigger signal, which is usually used in
        “Normal” and “Single” mode.
        """
        msg = ":FORC"
        self.dev.write(msg)

    ###################
    # 2. EDGE TRIGGER #
    ###################
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    """
    # EDGE TRIGGER 1
    def teSlope(self, positive=True):
        """
        The commands set and query the type of edge trigger. The type could be
        POSitive (Rising edge) or NEGative (Failing edge).
        """
        msg = ":TRIG:EDGE:SLOP {}".format("POS" if positive else "NEG")
        self.dev.write(msg)

    def askTeSlope(self):
        """
        The query returns POSITIVE or NEGATIVE.
        """
        msg = ":TRIG:EDGE:SLOP?"
        return self.dev.ask(msg)

    # EDGE TRIGGER 2
    def teSensitivity(self, count):
        """
        The commands set and query the sensitive of edge trigger. The range of
        <count> could be 0.1div~1div.
        """
        if count < .1 or count > 1:
            raise InvalidArgument("Count argument must be between .1 and 1")
        msg = ":TRIG:EDGE:SENS {}".format(count)
        self.dev.write(msg)

    def askTeSensitivity(self):
        """
        The query returns the setting value <count> in div.
        """
        msg = ":TRIG:EDGE:SENS?"
        return self.dev.ask(msg)

    ####################
    # 3. PULSE TRIGGER #
    ####################
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    """
    # PULSE TRIGGER 1
    def tpMode(self, mode):
        """
        The commands set and query the pulse condition. <mode> could be
        +GREaterthan (positive pulse greater than), +LESSthan (positive pulse less
        than), +EQUal (positive pulse equals to), -GREaterthan (negative pulse greater
        than), -LESSthan (negative pulse less than) or –EQUal (negative pulse equals
        to).
        """
        valid = ["+GRE", "+LESS", "-GRE", "-LESS", "+EQU", "-EQU"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}".format(valid))
        msg = ":TRIG:PULS:MODE {}".format(mode)
        self.dev.write(msg)

    def askTpMode(self):
        """
        The query returns +GREATER THAN, +LESS THAN, +EQUAL, -GREATER THAN,
        -LESS THAN or -EQUAL.
        """
        msg = ":TRIG:PULS:MODE?"
        return self.dev.ask(msg)

    # PULSE TRIGGER 2
    def tpSensitivity(self, count):
        """
        The commands set and query the sensitive of pulse trigger. The range of
        <count> could be 0.1div~1div.
        """
        if count < .1 or count > 1:
            raise InvalidArgument("Count argument must be between .1 and 1")
        msg = ":TRIG:PULS:SENS {}".format(count)
        self.dev.write(msg)

    def askTpSensitivity(self):
        """
        The query returns the setting value of <count> in div.
        """
        msg = ":TRIG:PULS:SENS?"
        return self.dev.ask(msg)

    # PULSE TRIGGER 3
    def tpWidth(self, width):
        """
        The commands set and query the pulse width. The range of <wid> is 20ns ~
        10s.
        """
        if width < .00000002 or width > 10:
            raise InvalidArgument("Width argument must be between 20ns and 10s")
        msg = ":TRIG:PULS:WIDT {}".format(width)
        self.dev.write(msg)

    def askTpWidth(self):
        """
        The query returns the setting value of the <wid> in s.
        """
        msg = ":TRIG:PULS:WIDT?"
        return self.dev.ask(msg)

    ####################
    # 4. VIDEO TRIGGER #
    ####################
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    """
    # VIDEO TRIGGER 1
    def tvMode(self, mode):
        """
        The commands set and query the synchronous mode of the video trigger.
        <mode> could be ODDfield, EVENfield, LINE or ALLlines.
        """
        valid = ["ODD", "EVEN", "LINE", "ALL"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid))
        msg = ":TRIG:VIDEO:MODE {}".format(mode)
        self.dev.write(msg)

    def askTvMode(self):
        """
        The query returns ODD FIELD, EVEN FIELD, LINE or ALL LINES.
        """
        msg = ":TRIG:VIDEO:MODE?"
        return self.dev.ask(msg)

    # VIDEO TRIGGER 2
    def tvPolarity(self, pos_polarity=True):
        """
        The commands set and query the video polarity. The polarity could be POSitive
        or NEGative.
        """
        msg = ":TRIG:VIDEO:POL {}".format("POS" if pos_polarity else "NEG")
        self.dev.write(msg)

    def askTvPolarity(self):
        """
        The query returns POSITIVE or NEGATIVE.
        """
        msg = ":TRIG:VIDEO:POL?"
        return self.dev.ask(msg)

    # VIDEO TRIGGER 3
    def tvStandard(self, ntsc=True):
        """
        The commands set and query the type of video trigger standard.
        """
        msg = ":TRIG:VIDEO:STAN {}".format("NTSC" if ntsc else "PALS")
        self.dev.write(msg)

    def askTvStandard(self):
        """
        The query returns NTSC or PAL/SECAM.
        """
        msg = ":TRIG:VIDEO:STAN?"
        return self.dev.ask(msg)

    # VIDEO TRIGGER 4
    def tvLine(self, value):
        """
        The commands set and query the number of specified line of synchronous. In
        NTSC standard, the range of <value> is 1~525; in PAL/SECAM standard, the
        range of <value> is 1~625.
        """
        standard = self.askTvStandard()
        if standard == "NTSC":
            if value < 1 or value > 525:
                raise InvalidArgument("When using {}, line value must be between 1 and 525.".format(standard))
        if standard == "PAL/SECAM":
            if value < 1 or value > 625:
                raise InvalidArgument("When using {}, line value must be between 1 and 625.".format(standard))
        msg = ":TRIG:VIDEO:LINE {}".format(value)
        self.dev.write(msg)

    def askTvLine(self):
        """
        """
        msg = ":TRIG:VIDEO:LINE?"
        return self.dev.ask(msg)

    # VIDEO TRIGGER 5
    def tvSensitivity(self, count):
        """
        The commands set and query the trigger sensitive, the range of <count> is:
        0.1div ~1div.
        """
        if count < .1 or count > 1:
            raise InvalidArgument("Count argument must be between .1 and 1.")
        msg = ":TRIG:VIDEO:SENS {}".format(count)
        self.dev.write(msg)

    def askTvSensitivity(self):
        """
        The query returns the setting value of <count> in div.
        """
        msg = ":TRIG:VIDEO:SENS?"
        return self.dev.ask(msg)

    ####################
    # 5. SLOPE TRIGGER #
    ####################
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    6 - yes
    """
    # SLOPE TRIGGER 1
    def tsTime(self, count):
        """
        The commands set and query the time setting about slope trigger. The range of
        <count> is 20ns~10s.
        """
        if count < .00000002 or count > 10:
            raise InvalidArgument("Count argument must be between 20ns and 10s.")
        msg = ":TRIG:SLOP:TIME {}".format(count)
        self.dev.write(msg)

    def askTsTime(self):
        """
        The query returns the setting value of <count> in s.
        """
        msg = ":TRIG:SLOP:TIME?"
        return self.dev.ask(msg)

    # SLOPE TRIGGER 2
    def tsSensitivity(self, count):
        """
        The commands set and query the trigger sensitive. The range of <count> is:
        0.1div ~1div.
        """
        if count < .1 or count > 1:
            raise InvalidArgument("Count argument must be between .1 and 1.")
        msg = ":TRIG:SLOP:SENS {}".format(count)
        self.dev.write(msg)

    def askTsSensitivity(self):
        """
        The query returns the setting value of <count> in div.
        """
        msg = ":TRIG:SLOP:SENS?"
        return self.dev.ask(msg)

    # SLOPE TRIGGER 3
    def tsMode(self, mode):
        """
        The commands set and query the slope condition. <mode> could be
        +GREaterthan (positive slope greater than), +LESSthan (positive slope less
        than), + EQUal (positive slope equals to), -GREaterthan (negative slope greater
        than), -LESSthan (negative slope less than) or –EQUal (negative slope equals
        to).
        """
        valid = ["+GRE", "+LESS", "+EQU", "-GRE", "-LESS", "-EQU"]
        if mode not in valid:
            raise InvalidArgument("Mode must be one of {}.".format(valid))
        msg = ":TRIG:SLOP:MODE {}".format(mode)
        self.dev.write(msg)

    def askTsMode(self):
        """
        The query returns +GREATER THAN, +LESS THAN, +EQUAL, -GREATER THAN,
        -LESS THAN OR -EQUAL.
        """
        msg = ":TRIG:SLOP:MODE?"
        return self.dev.ask(msg)

    # SLOPE TRIGGER 4
    def tsWindow(self, count):
        """
        The commands set and query the type of trigger level which can be adjusted by
        the level knob on the oscilloscope.
        When the slope condition is +GREaterthan, +LESSthan or + EQUal, <count>
        could be PA (rising edge Level A), PB (rising edge Level B) or PAB (rising edge
        Level AB);
        When the slope condition is -GREaterthan, -LESSthan or –EQUal, <count> could
        be NA (falling edge Level A), NB (falling edge LevelB) or NAB (falling edge
        LevelAB).
        """
        trig_mode = self.askTsMode()
        if "+" in trig_mode:
            valid = ["PA", "PB", "PAB"]
            if count not in valid:
                raise InvalidArgument("While trigger mode is {}, count argument must be one of {}.".format(valid))
        if "-" in trig_mode:
            valid = ["NA", "NB", "NAB"]
            if count not in valid:
                raise InvalidArgument("While trigger mode is {}, count argument must be one of {}.".format(valid))
        msg = ":TRIG:SLOP:WIND {}".format(count)
        self.dev.write(msg)

    def askTsWindow(self):
        """
        The query returns P_WIN_A, P_WIN_B, P_WIN_AB, N_WIN_A, N_WIN_B or
        N_WIN_AB.
        """
        msg = ":TRIG:SLOP:WIND?"
        return self.dev.ask(msg)

    # SLOPE TRIGGER 5
    def tsLevelA(self, value):
        """
        The commands set and query the upper boundary “Level A” of trigger level. The
        range of <value> is LevelB~+ 6*Scale; Scale indicates the current vertical level,
        the unit is V/div.
        """
        # Not checking for valid inputs but should be implemented
        msg = ":TRIG:SLOP:LEVA {}".format(value)
        self.dev.write(msg)

    def askTsLevelA(self):
        """
        The query returns the setting value of level in V.
        """
        msg = ":TRIG:SLOP:LEVA?"
        return self.dev.ask(msg)

    # SLOPE TRIGGER 6
    def tsLevelB(self, value):
        """
        The commands set and query the lower boundary “LEVel B” of trigger level. The
        range of <value> is -6*Scale~LevelA; Scale indicates the current vertical level,
        the unit is V/div.
        """
        # Not checking for valid inputs but should be implemented
        msg = ":TRIG:SLOP:LEVB {}".format(value)
        self.dev.write(msg)

    def askTsLevelB(self):
        """
        The query returns the setting value of level in V.
        Note: Level A (upper boundary) can not be less than the maximum of Level B
        (lower boundary).        """
        msg = ":TRIG:SLOP:LEVB?"
        return self.dev.ask(msg)

    # PATTERN TRIGGER IS NOT A FEATURE ON THE DS1000E SERIES

    # DURATION TRIGGER IS NOT A FEATURE ON THE DS1000E SERIES

    ##########################
    # 8. ALTERNATION TRIGGER #
    ##########################
    """
    not implemented
    """

    ########
    # MATH #
    ########
    """
    not implemented
    """

    ###########
    # CHANNEL #
    ###########
    """
    fully implemented
    1 - yes
    2 - yes
    3 - yes
    4 - yes
    5 - yes
    6 - yes
    7 - yes
    8 - yes
    9 - yes
    10 - yes
    """

    # CHANNEL 1
    def channelBwlimit(self, channel, on=True):
        """
        The commands set and query the On/Off state of bandwidth limit. <n> could be
        1 or 2.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel argument must be either {}.".format([1, 2]))
        msg = ":CHAN{}:BWL {}".format(channel, "ON" if on else "OFF")
        self.dev.write(msg)

    def askChannelBwlimit(self, channel):
        """
        The query returns ON or OFF.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel argument must be either {}.".format([1, 2]))
        msg = ":CHAN{}:BWL?"
        return self.ask(msg)

    # CHANNEL 2
    def channelCoupling(self, channel, coupling):
        """
        The commands set and query the coupling mode of channel. DC indicates both
        the AC and DC components passed from input signal; AC indicates the blocked
        DC components; GND indicates to cut off the input of signal; <n> could be 1 or
        2.
        """
        valid = ["AC", "DC", "GND"]
        if coupling not in valid:
            raise InvalidArgument("Coupling argument must be one of {}.".format(valid))
        if channel not in [1, 2]:
            raise InvalidArgument("Channel argument must be one of {}.".format([1, 2]))
        msg = ":CHAN{}:COUP {}".format(channel, coupling)
        self.dev.write(msg)

    def askChannelCoupling(self, channel):
        """
        The query returns AC, DC or GND.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel argument must be one of {}.".format([1, 2]))
        msg = ":CHAN{}:COUP?".format(channel)
        return self.dev.ask(msg)

    # CHANNEL 3
    def channelDisplay(self, channel, on=True):
        """
        channel - either 1 or 2
        on - boolean value for turning the display on or off for the given channel.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        self.dev.write(":CHAN{}:DISP {}".format(channel, "ON" if on else "OFF"))

    def askChannelDisplay(self, channel):
        """
        The query returns ON or OFF.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        self.dev.write(":CHAN{}:DISP?".format(channel))

    # CHANNEL 4
    def channelInvert(self, channel, on=True):
        """
        The commands set and query the On/Off state of the waveform inverted. <n>
        could be 1 or 2.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:INV {}".format(channel, "ON" if on else "OFF")
        self.dev.write(msg)

    def askChannelInvert(self, channel):
        """
        The query returns ON or OFF.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:INV?".format(channel)
        return self.dev.ask(msg)

    # CHANNEL 5
    def channelOffset(self, channel, offset):
        """
        The commands set and query the vertical offset. <n> could be 1 or 2.
        When Scale≥250mV, the range of <offset>is -40V~+40V;
        When Scale<250mV, the range of <offset>is -2V~+2V.
        """
        # not checking for valid offset inputs
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:OFFS {}".format(channel, offset)
        self.dev.write(msg)
        if channel == 1:
            self.volt1_offset = self.askChannelOffset(1)
        elif channel == 2:
            self.volt2_offset = self.askChannelOffset(2)

    def askChannelOffset(self, channel):
        """
        The query returns the setting value of <offset>.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:OFFS?".format(channel)
        offset = float(self.dev.ask(msg))
        if channel == 1:
            self.volt1_offset = offset
        elif channel == 2:
            self.volt2_offset = offset
        return float(offset)

    # CHANNEL 6
    def channelProbe(self, channel, attn):
        """
        The commands set and query the attenuation factor of the probe. <n> could be
        1 or 2; <attn> could be 1, 5, 10, 50, 100, 500 or 1000.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        valid_attn = [1, 5, 10, 50, 100, 500, 1000]
        if attn not in valid_attn:
            raise InvalidArgument("Attn argument must be one of {}".format(valid_attn))
        msg = ":CHAN{}:PROB {}".format(channel, attn)
        self.dev.write(msg)

    def askChannelProbe(self, channel):
        """
        The query returns the setting value of <attn>.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:PROB?".format(channel)
        return self.dev.ask(msg)

    # CHANNEL 7
    def channelScale(self, channel, v):
        """
        channel - Which channel to scale.
        v - voltage scale
        The commands set and query the vertical scale of waveform magnified by the
        oscilloscope. <n> could be 1 or 2.
        When the Probe is set to 1X, the range of <range> is 2mV ~ 10V;
        When the Probe is set to 5X, the range of <range> is 10mV ~50V;
        When the Probe is set to 10X, the range of <range> is 20mV ~ 100V;
        When the Probe is set to 50X, the range of <range> is 100mV ~ 500V;
        When the Probe is set to 100X, the range of <range> is 200mV ~ 1000V;
        When the Probe is set to 500X, the range of <range> is 1V ~5000V;
        When the Probe is set to 1000X, the range of <range> is 2V~ 10000V.
        """
        # not error checking scale value
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:SCAL {}".format(channel, v)
        self.dev.write(msg)
        if channel == 1:
            self.volt1_scale = self.askChannelScale(1)
        elif channel == 2:
            self.volt2_scale = self.askChannelScale(2)

    def askChannelScale(self, channel):
        """
        query what the scale is for channel <channel>
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:SCAL?".format(channel)
        scale = float(self.dev.ask(msg))
        if channel == 1:
            self.volt1_scale = scale
        elif channel == 2:
            self.volt2_scale = scale
        return scale

    # CHANNEL 8
    def channelFilter(self, channel, on=True):
        """
        The commands set and query the On/Off state of the filter. <n> could be 1 or 2.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = "CHAN{}:FILT {}".format(channel, "ON" if on else "OFF")
        self.dev.write(msg)

    def askChannelFilter(self, channel):
        """
        The query returns ON or OFF.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:FILT?".format(channel)
        return self.dev.ask(msg)

    # CHANNEL 9
    def askChannelMemoryDepth(self, channel):
        """
        The command queries the memory depth of the specified channel. <n> could
        be 1 or 2.
        In long memory, up to 1Mpts could be stored in single channel and 512kpts in
        dual channels;
        In common memory, up to 16kpts could be stored in single channel and 8kpts in
        dual channels.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:MEMD?".format(channel)
        return self.dev.ask(msg)

    # CHANNEL 10
    def channelVernier(self, channel, on=True):
        """
        The commands set and query the adjusting mode of scale. ON denotes Fine,
        OFF denotes Coarse; <n> could be 1 or 2.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        msg = ":CHAN{}:VERN {}".format(channel, "ON" if on else "OFF")
        self.dev.write(msg)

    def askChannelVernier(self, channel):
        """
        The query returns Coarse or Fine.
        """
        msg = ":CHAN{}:VERN?".format(channel)
        return self.dev.ask(msg)

    ###########
    # MEASURE #
    ###########
    """
    partially implemented
    1 - no
    2 - yes
    3 - no
    .
    .
    .
    23 - yes
    """

    def measureVpp(self, channel):
        """
        channel is either 1 or 2
        returns peak to peak voltage in Volts.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel argument must be either 1 or 2")
        msg = ":MEAS:VPP? CHAN{}".format(channel)
        return float(self.dev.ask(msg))

    ############
    # WAVEFORM #
    ############
    """
    partially implemented
    1 - yes
    """

    # WAVEFORM 1
    def askWaveformData(self, source):
        """
        returns 1024 data for <source>.  Raw Data.
        run through numpy.frombuffer(data, "B") to get point data
        First 10 bytes are apparently a header, so we can skip those.
        """
        valid_sources = ["CHAN1", "CHAN2", "DIG", "MATH", "FFT"]
        if source not in valid_sources:
            raise InvalidArgument("Source argument must be one of {}".format(valid_sources))
        msg = ":WAV:DATA? {}".format(source)
        # self.dev.read()
        # self.dev.write(msg)
        # return self.dev.read_raw()
        return self.dev.ask_raw(msg)[10:]

    # WAVEFORM 2
    def waveformPointsMode(self, mode):
        """
        This command sets the mode of waveform points. <points_mode> can be:
        NORMal, MAXimum or RAW.
        """
        valid = ["NORM", "MAX", "RAW"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid))
        msg = ":WAV:POIN:MODE {}".format(mode)
        self.dev.write(msg)

    def askWaveformPointsMode(self):
        """
        The query returns NORMal, MAXimum or RAW.
        """
        msg = ":WAV:POIN:MODE?"
        return self.dev.ask(msg)

    ###################
    # CUSTOM WAVEFORM #
    ###################
    def getWaveform(self, source):
        """
        The data that is extracted from the oscilloscope needs to be inverted,
            multiplied by a constant and shifted by some voltage offset to get the
            true values.
        A custom method for retrieving the corrected voltage values out of the
            oscilloscope.
        """
        raw_data = self.askWaveformData(source)
        raw_data = np.frombuffer(raw_data, "B")
        data = self.convertVoltages(raw_data, source)
        return data

    def convertVoltages(self, data, source):
        """
        data - numpy array of unconverted voltage values.
        """
        if source == "CHAN1":
            data = -data + 255
            data = (data - 130.0 - self.volt1_offset/self.volt1_scale*25) / 25 * self.volt1_scale
        elif source == "CHAN2":
            data = -data + 255
            data = (data - 130.0 - self.volt2_offset/self.volt2_scale*25) / 25 * self.volt2_scale
        return data

    def getTimebase(self):
        """
        get correct x-values for plotting waveform
        """
        time_axis = np.arange(-300.0/50*self.time_scale, 300.0/50*self.time_scale, self.time_scale/50.0)
        return time_axis

    #######
    # KEY #
    #######
    """
    not enabled
    """
    def keyLock(self, enable=True):
        """
        This command is used to enable/disable the buttons function on the front panel
        (except for “Force”).
        """
        msg = ":KEY:LOCK {}".format("ENAB" if enable else "DIS")
        self.dev.write(msg)

    def askKeyLock(self):
        """
        The query returns ENABLE or DISABLE.
        """
        msg = "KEY:LOCK?"
        return self.dev.ask(msg)

    ######################
    # CUSTOM SAVE STATES #
    ######################
    """
    Some methods to query many settings of the oscilloscope and then
        load saved settings from the computer.
    """

    # UNFINISHED
    def saveState(self):
        """
        Queries the state of the oscilloscope and saves it as a python list string
            formatted file to a location of your choosing through tkFileDialog.
        """
        save_location = tkfd.asksaveasfilename(defaultextension=".ros", filetypes=[("Rigol Oscilloscope Save", "*.ros")])
        s = []
        acquire_type = self.askAcquireType()[:4]
        s.append(":ACQ:TYPE {}".format(acquire_type))
        aquire_mode = self.askAquireMode()
        aquire_mode = "RTIM" if aquire_mode[0] == "R" else "ETIM"
        s.append(":ACQ:MODE {}".format(aquire_mode))
        memdepth = self.askAcquireMemDepth()[:4]
        s.append(":ACQ:MEMD {}".format(memdepth))
        disptype = self.askDisplayType()[:4]
        s.append(":DISP:TYPE {}".format(disptype))
        dispgrid = self.askDisplayGrid()
        s.append(":DISP:GRID {}".format(dispgrid))
        disppersisty = self.askDisplayPersist()
        s.append(":DISP:PERS {}".format(disppersisty))
        dispbrightness = self.askDisplayBrightness()
        s.append(":DISP:BRIG {}".format(dispbrightness))
        dispintensity = self.askDisplayIntensity()
        s.append(":DISP:INT {}".format(dispintensity))
        timemode = self.askTimebaseMode()
        timemode = "DEL" if timemode == "DELAYED" else timemode
        s.append(":TIM:MODE {}".format(timemode))
        delayed = True if timemode == "DEL" else False
        timeoffset = self.askTimebaseMode(delayed=delayed)
        s.append(":TIM{}:OFFS {}".format(":DEL" if delayed else "", timeoffset))
        timescale = self.askTimebaseScale(delayed=delayed)
        s.append(":TIM{}:SCAL {}".format(":DEL" if delayed else "", timescale))
        timeformat = self.askTimebaseFormat()
        s.append(":TIM:FORM {}".format(timeformat))
        #  continue with trigger settings

        #  Write file to save_location
        with open(save_location, "w") as f:
            f.write(str(s))

    def loadState(self):
        """
        writes the commands in the .ros save list.
        """
        load_file = tkfd.askopenfilename(
            defaultextension=".ros",
            filetypes=[("Rigol Oscilloscope Save", "*.ros")],
            title="Rigol Oscilloscope Save file to load"
            )
        with open(load_file, "r") as f:
            state_str = f.read().strip()
            state = ast.literal_eval(state_str)
            for setting in state:
                self.dev.write(setting)
        print("{} save state has been loaded".format(load_file))
