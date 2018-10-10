# A Python Serial logger implementation using observer pattern
The main.py show cases using observer pattern (python-observer package) to read from a serial
port (real or fake) and provides a CLI for logging to console or file by offering different
options. In addition, this application also shows a de-coupled and cohesive design that is
very flexible.

Run the CLI in your terminal for help instructions:
```console
$ python main.py -h
```

For example writing to console and log file from fake serial port at the same time with debug printing:
```console
$ python main.py -d -f -p COM1 -l
```

## Prerequisites

OBS! Works for both Python2.6+ only!
Install [python](https://www.python.org/downloads/)

Install [pySerial](https://github.com/pyserial/pyserial/blob/master/documentation/pyserial.rst)

Get python-observer package by issuing the following command:
```console
$ pip install git+https://github.com/FrederikBjorne/python-observer.git
```
