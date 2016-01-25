"""
rigol.py
University of Oregon - Advanced Physics Lab
Built on top of rigolSkeleton.py to control the rigol ds 1000d/e
    series oscilloscopes

Using this programming guide -> http://www.batronix.com/pdf/Rigol/ProgrammingGuide/DS1000DE_ProgrammingGuide_EN.pdf
"""
from __future__ import division
import rigolSkeleton as rs

__author__ = "Brian Perrett"


class InvalidBackendException(Exception):
    pass


class InvalidArgument(Exception):
    pass


class Rigol:

    backends = ["usbtmc"]

    def __init__(self, backend, idProduct=None, idVendor=None):
        if backend == "usbtmc":
            self.dev = rs.RigolSkeleton(idProduct=idProduct, idVendor=idVendor)
        else:
            raise InvalidBackendException("Please specify a valid backend such as {}".format(self.backends))

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

    def askTimebaseOffset(self, delayed=False):
        """
        The query returns the setting value of the <offset> in s.
        """
        msg = ":TIM{}:OFFS?".format(":DEL" if delayed else "")
        return self.dev.ask(msg)

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

    def askTimebaseScale(self, delayed=False):
        """
        The query returns the setting value of <scale_val> in s.
        """
        msg = ":TIM{}:SCAL?".format(":DEL" if delayed else "")
        return self.dev.ask(msg)

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
    not implemented
    """

    ####################
    # 5. SLOPE TRIGGER #
    ####################
    """
    not implemented
    """

    ######################
    # 6. PATTERN TRIGGER #
    ######################
    """
    not implemented
    """

    #######################
    # 7. DURATION TRIGGER #
    #######################
    """
    not implemented
    """

    ##########################
    # 8. ALTERNATION TRIGGER #
    ##########################
    """
    not implemented
    """

    ###########
    # CHANNEL #
    ###########
    """
    partially implemented
    1 - no
    2 - no
    3 - yes
    4 - no
    .
    .
    .
    """

    def channelDisplay(self, channel, on=True):
        """
        channel - either 1 or 2
        on - boolean value for turning the display on or off for the given channel.
        """
        if channel not in [1, 2]:
            raise InvalidArgument("Channel must take a value from {}.".format([1, 2]))
        self.dev.write(":CHAN{}:DISP {}".format(channel, "ON" if on else "OFF"))

    def channelScale(self, channel, v):
        """
        channel - Which channel to scale.
        v - voltage scale
        """
        msg = ":CHAN{}:SCAL {}".format(channel, v)
        self.dev.write(msg)

    def askChannelScale(self, channel):
        """
        query what the scale is for channel <channel>
        """
        msg = ":CHAN{}:SCAL?".format(channel)
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
        return self.dev.ask(msg)

    ############
    # WAVEFORM #
    ############
    """
    partially implemented
    1 - yes
    """

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

    def waveformPointsMode(self, mode):
        """
        """
        valid = ["NORM", "MAX", "RAW"]
        if mode not in valid:
            raise InvalidArgument("Mode argument must be one of {}.".format(valid))
        msg = ":WAV:POIN:MODE {}".format(mode)
        self.dev.write(msg)
