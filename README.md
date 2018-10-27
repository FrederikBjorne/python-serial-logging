# A Python Serial logger implementation and serial port CLI using observer pattern
The file main.py show cases an application using observer pattern (python-observer package) to
read from a serial port (real or fake) and provides a CLI for logging to console (always on) and
file by offering different options. Using python-observer package, renders a de-coupled and
cohesive design that is very flexible and easy to maintain.

The serial reader- and file writer threads uses callbacks for communicating with the application
if they fail. The program waits for the user to enter any key to quit the program.

Run the serial logger CLI in your terminal for help instructions:
```console
$ python main.py -h
usage: 
  main.py -p COM1
  main.py -p COM1 -l serial.txt -t -f

Serial Logger CLI

You log from a serial port set by name. The serial stream is logged to console.
Writing the stream to a file is an option. A fake serial stream is an option
too and typically useful for development or unit testing with fault-injection.
Hit any key to quit the program.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           set debug log level
  -l LOGFILE, --logfile LOGFILE
                        set log to file
  -f, --fake            set fake serial
  -p PORT, --port PORT  set serial port
  -t, --timestamp       add timestamp in logging
```

For example writing to console and log file from fake serial port at the same time with debug printing:
```console
$ python main.py -p COM1 -f -l serial.txt
```

### List ports
Run the serial port helper CLI in your terminal for help instructions:
```console
$ python serialporthelper.py -h
usage: 
  serialporthelper.py -l
  serialporthelper.py -p COM1

List serial ports CLI

optional arguments:
  -h, --help            show this help message and exit
  -l, --listports       list serial ports
  -p PORT, --port PORT  check if a port is available
```

## Prerequisites

OBS! Works for Python2.6+ only!
Install [python](https://www.python.org/downloads/)

Install [pySerial](https://github.com/pyserial/pyserial/blob/master/documentation/pyserial.rst)

Install [python-observer](https://github.com/FrederikBjorne/python-observer) package.

## Limitations
The serial logger CLI program currently only works for serial ports over usb, since it does not provide
any port configuration. However, you may always change the call to Serial in main.py to your special
needed settings.
