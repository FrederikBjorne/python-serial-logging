#!/usr/bin/env python

from sys import platform
from sys import stdout
import logging

from observer import Observer
from serialporthelper import SerialPortHelper
from serialreader import SerialReader
from filewriter import FileWriter


class SerialFileWriter(Observer):
    """
    This class intercepts logs and writes these to its own file writer.
    """

    def __init__(self, log_file_path, callback):
        self.logger = logging.getLogger(self.__class__.__name__)
        super(SerialFileWriter, self).__init__(self.__class__.__name__)
        self._file_writer = FileWriter(log_file_path, callback)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.name)

    def start(self):
        self._file_writer.start()

    def stop(self):
        self._file_writer.stop()

    def is_alive(self):
        return self._file_writer.is_alive()

    def update(self, data):
        log_line = data[0]  # data is a tuple
        if self._file_writer.is_alive():
            self.logger.debug('writing: {}'.format(log_line))
            self._file_writer.put(log_line)  # log lines are written to file writer's queue


class SerialPrinter(Observer):
    """
    Simply intercepts logs and prints these to the console.
    """
    def __init__(self):
        super(SerialPrinter, self).__init__(self.__class__.__name__)
        self.logger = logging.getLogger(self.name)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.name)

    def update(self, new_data):
        log_line = new_data[0]  # new_data is a tuple
        print('{}\r'.format(log_line))


def check_for_any_key_to_quit():
    root_logger.info('Stop by entering a key.')
    if platform.startswith('win32'):  # on windows machines
        from msvcrt import kbhit, getch
        while True:
            if kbhit():
                return getch()
    else:  # on any unix machine including mac osx
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)  # wait for any one key input
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


if __name__ == "__main__":
    import argparse
    from os.path import basename

    # CLI
    program_name = basename(__file__)
    parser = argparse.ArgumentParser(description=('Serial Logger CLI\n\n'
                                                  'You log from a serial port set by name. '
                                                  'The serial stream is logged to console.\n'
                                                  'Writing the stream to a file is an option.\n'
                                                  'A fake serial stream is an option too and '
                                                  'typically useful for development or\n'
                                                  'unit testing with fault-injection.\n'
                                                  'Hit any key to quit the program.\n'),
                                     prog = program_name,
                                     epilog = ('\n  %(prog)s -p COM1\n'
                                               '  %(prog)s -p COM1 -f -l serial.txt\n'),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--debug', default=False, help='set debug log level', action='store_true')
    parser.add_argument('-l', '--logfile', type=str, help='set log to file')
    parser.add_argument('-f', '--fake', default=False, help='set fake serial', action='store_true')
    parser.add_argument('-p', '--port', type=str, required = True, help = 'set serial port')
    parser.add_argument('-t', '--timestamp', default=False, help='add timestamp in logging', action='store_true')
    args = parser.parse_args()

    (debug_print,
     log_file,
     fake_serial,
     port_name,
     timestamp) = args.debug, args.logfile, args.fake, args.port, args.timestamp

    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(name)-18s %(levelname)-8s %(message)s\r'))

    # Add the console handler to the root logger for default
    root_logger = logging.getLogger()
    root_logger.setLevel(level = logging.DEBUG if debug_print else logging.INFO)
    file_logger = root_logger.addHandler(console_handler)

    if fake_serial:
        from fakeserial import Serial, FAKE_LOG
        Serial.prepare(fake_serial_stream = FAKE_LOG)
    else:
        from serial import Serial
        SerialPortHelper.check_port(port_name)

    # Open the serial port specified by port name
    with Serial(port = port_name, baudrate = 115200, timeout = 1) as serial_port:

        def error_handler(error_string):
            root_logger.error('error: {}'.format(error_string))
            root_logger.error('Program has failed operation, so hit any key to quit please!')

        file_writer, reader = None, None
        try:
            reader = SerialReader(serial = serial_port, callback = error_handler, do_timestamp = timestamp)

            if log_file:
                def write_error_handler(error_string):
                    reader.detach(file_writer)
                    error_handler(error_string)

                file_writer = SerialFileWriter(log_file_path = log_file, callback = write_error_handler)
                reader.attach(file_writer)
                file_writer.start()

            reader.attach(SerialPrinter())  # printing to console is always on

            reader.start()

            check_for_any_key_to_quit()
        finally:
            # tear down serial reader and file writer threads before exiting
            if reader.is_alive():
                reader.stop()

            if file_writer and file_writer.is_alive():
                file_writer.stop()
