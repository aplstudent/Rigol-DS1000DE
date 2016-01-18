"""
rigolSkeleton.py
Brian Perrett
Advanced Projects Lab, University of Oregon
January 12, 2016

to be used on top of other classes as the means of writing commands
    to and retrieving from the Rigol DS1102E
Add more classes to add more backends.

Written and tested in python2.7 on Ubuntu 15.10
"""
import usbtmc


class RigolSkeleton():
    """
    USBTMC BACKEND
    A wrapper of the usbtmc library.  The idea is that I can create an
        abstraction layer so that in the future, I can write other backends
        to support other os's.  May need to make a pyvisa backend, for example.
    """
    def __init__(self, idProduct=None, idVendor=None):
        """
        """
        self.instr = self.connect(idProduct, idVendor)
        print("Asking *IDN? returns: {}".format(self.ask("*IDN?")))

    def connect(self, idProduct=None, idVendor=None):
        """
        if either idProduct or idVendor are None, query the user for what to connect to.
        """
        if idProduct is None or idVendor is None:
            for dev in usbtmc.list_devices():
                print("1: {} - {}".format(dev.manufacturer, dev.product))
            dev_con = raw_input("Enter the number of the device you want to connect to: ")
            dev_chosen = usbtmc.list_devices()[int(dev_con) - 1]
            product_id = dev_chosen.idProduct
            vendor_id = dev_chosen.idVendor
        instr = usbtmc.Instrument(vendor_id, product_id)
        return instr

    def read(self, num=-1, encoding="utf-8"):
        """
        Wrapping around the read method in usbtmc.Instrument
        """
        return self.instr.read(num, encoding)

    def write(self, message, encoding="utf-8"):
        """
        Wrapping around the write method in usbtmc.Instrument
        """
        return self.instr.write(message, encoding)

    def ask(self, message, num=-1, encoding="utf-8"):
        """
        Wrapping around the ask method in usbtmc.Instrument
        """
        return self.instr.ask(message, num, encoding)


def testConnect():
    rigol = RigolSkeleton()

if __name__ == '__main__':
    testConnect()