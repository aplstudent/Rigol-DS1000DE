"""
rigol.py
University of Oregon - Advanced Physics Lab
Built on top of rigolSkeleton.py to control the rigol ds 1000d/e
    series oscilloscopes
"""
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
    # DISPLAY #
    ###########
    def brightness(self, level):
        """
        Changes the brightness level of the grid.
        level - Brightness level from 0 to 32
        """
        if level < 0 or level > 32:
            raise InvalidArgument("Level argument must be between 0 and 32.")
        self.dev.write(":DISP:BRIG {}".format(level))

    def askBrightness(self):
        """
        query the brightness of the grid
        returns a string from 0 to 32
        """
        return self.dev.ask(":DISP:BRIG?")

    def intensity(self, level):
        """
        level - intensity level from 0 to 32
        """
        if level < 0 or level > 32:
            raise InvalidArgument("level argument must be between 0 and 8.")
        self.dev.write(":DISP:INT {}".format(level))

    def askIntensity(self):
        """
        Returns waveform brightness from 0 to 32
        """
        return self.dev.ask(":DISP:INT?")

    ###########
    # TRIGGER #
    ###########
    """
    Which trigger functions have been implemented.
    Numbering is based off of numbering in the programming manual.
    1 - yes
    2 - yes
    3 - no
    4 - no
    5 - no
    6 - no
    7 - no
    8 - no
    9 - no
    """

    # TRIGGER 1
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

    # TRIGGER 2
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

    ###########
    # CHANNEL #
    ###########
    """
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