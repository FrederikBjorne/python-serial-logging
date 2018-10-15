# A Python Serial logger implementation using observer pattern
The file main.py show cases using observer pattern (py-observer package) to read from a serial port
(real or fake) and provides a CLI for logging to console or/and file by offering different options.
The serial reader- and file writer threads uses callbacks for communicating with the application
when they have failed. The program waits for the user to enter a any key to quit the program.

In addition, this application show cases a de-coupled and cohesive design that is very flexible.

Run the CLI in your terminal for help instructions:
```console
$ python main.py -h
```

For example writing to console and log file from fake serial port at the same time with debug printing:
```console
$ python main.py -d -f -p COM1 -l
```

## Prerequisites

OBS! Works for Python2.6+ only!
Install [python](https://www.python.org/downloads/)

Install [pySerial](https://github.com/pyserial/pyserial/blob/master/documentation/pyserial.rst)

Install [python-observer](https://github.com/FrederikBjorne/python-observer) package.
