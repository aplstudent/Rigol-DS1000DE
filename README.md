# Rigol-DS1000DE
The files in the Rigol-DS1000DE repository provide a convenient way for python users to communicate with the DS1000D/E series of Rigol Oscilloscopes.
Currently it uses python-usbtmc as its backend for usb communication with the oscilloscope, but other backends could be added in the usbcon.py file.

### Installation on Ubuntu
Currently, the only OS that I have tested this on is Ubuntu, but I imagine it would work on other linux operating systems, and if you can get usbtmc working on windows, it may work there as well.

* Make sure you are running python 2.7.  I wrote this with compatibility with python 3 in mind, but I have not tested it.
* Download this repo
* Install usbtmc

`$ sudo apt-get install python-usbtmc`

* Be sure libusb-1.0 is installed

`$ sudo apt-get install libusb-1.0-0`

* Install numpy

`$ sudo apt-get install numpy`

#### Setting Usb Permissions
* As per the suggestion of http://scruss.com/blog/tag/usbtmc/ we add ourselves to a group which has permissions to access our usb device.

`$ sudo groupadd usbtmc`

* Add yourself to the group.

`$ sudo usermod -a -G usbtmc <user>`

* As root, create a file /etc/udev/rules.d/usbtmc.rules. You’ll need to put in your device’s ID values.  If you don't know the id values, check the "Finding your devices ID Values" section.
    ```python
    # USBTMC instruments
    # Rigol DS1100 – ID 1ab1:0588 Rigol Technologies DS1000 SERIES
    SUBSYSTEMS==”usb”, ACTION==”add”, ATTRS{idVendor}=="1ab1", ATTRS{idProduct}=="0588", GROUP="usbtmc", MODE="0660"
    ```

* We also need pyusb

`pip install pyusb` or `pip install --pre pyusb`

#### Finding Your Devices ID Values

* If the only think that you haven't done of the above is find your USB ID values, then you should be able to:
 * Be sure that the oscilloscope is connected
 * Run the following as superuser:

`$ sudo python`

```python
import usbtmc
devices = usbtmc.list_devices()
for dev in devices:
    print(dev.manufacturer)
    print(dev.idProduct)
    print(dev.idVendor)
```

When this is run, it should return a list of available devices and you will see the product and vendor id's

## Usage
* View the [ipython notebook](https://github.com/aplstudent/Rigol-DS1000DE/blob/master/Usage%20and%20Examples.ipynb) I've written to see what kinds of methods are available inside of rigol.py.  The examples are not exhaustive and if you want to see what is available to you, open up the rigol.py file to see the source code.

### Running the GUI
* Run the interface file - Still must be done in superuser mode so that you have access to the usb device.

`$ sudo python rigolx.py`

#### Sources Used

Using this programming guide -> http://www.batronix.com/pdf/Rigol/ProgrammingGuide/DS1000DE\_ProgrammingGuide\_EN.pdf

- http://scruss.com/blog/tag/usbtmc/
- http://www.righto.com/2013/07/rigol-oscilloscope-hacks-with-python.html
- http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/