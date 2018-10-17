#!/usr/bin/env python
import select
from sys import platform
from sys import stdout
from threading import Event
import logging

from observer import Observer
from serialreader import SerialReader
from filewriter import FileWriter


class SerialFileWriter(Observer):
    """
    This class intercepts logs and writes these to its own file writer.
    """
    logger = logging.getLogger('SerialFileWriter')

    def __init__(self, log_file_path, callback):
        super(SerialFileWriter, self).__init__('SerialFileWriter')
        self._file_writer = FileWriter(log_file_path, callback)

    def __repr__(self):
        return '{}({!r}'.format(self.__class__.__name__, self.name)

    def start(self):
        self._file_writer.start()

    def stop(self):
        self._file_writer.stop()
        self._file_writer.join()

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
        super(SerialPrinter, self).__init__('SerialPrinter')
        self.logger = logging.getLogger(self.name)

    def __repr__(self):
        return '{}({!r}'.format(self.__class__.__name__, self.name)

    def update(self, new_data):
        log_line = new_data[0]  # new_data is a tuple
        self.logger.debug('printing {}'.format(log_line))


def check_port(port_name):
    """
    Checks that the serial port is available.
    :param port_name: The port name as a string
    :raises SerialException if port is not detected.
    """
    # This requires pyserial version > 2.6 that has a bug with showing serial ports.
    ports = [str(port).split('-')[0].strip() for port in list_ports.comports()]
    if port_name not in ports:
        raise SerialException('Port {} not found. Check spelling of port name.'
                              .format(port_name))


def wait_for_any_key_to_quit():
    root_logger.info('Stop by entering a key.')
    if platform.startswith('win32'):  # on windows machines
        from msvcrt import kbhit, getch
        while True:
            if kbhit():
                return getch()
    else:  # on any unix machine
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
    prog = basename(__file__)
    parser = argparse.ArgumentParser(description='SerialReader CLI',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=('Example of use:\n'
                                             '  {0} -d -p COM1\n'
                                             '  {0}-f -p COM1\n').format(prog))
    parser.add_argument('-d', '--debug', default=False, help='Set debug log level', action='store_true')
    parser.add_argument('-l', '--logfile', default=False, help='Set log to file', action='store_true')
    parser.add_argument('-f', '--fake', default=False, help='Set fake serial', action='store_true')
    parser.add_argument('-p', '--port', type = str, required = True, help = 'Name of serial port')
    args = parser.parse_args()

    debug_print, log_to_file, fake_serial, port_name = args.debug, args.logfile, args.fake, args.port

    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(name)-18s %(levelname)-8s %(message)s'))

    # Add the console handler to the root logger for default
    root_logger = logging.getLogger()
    root_logger.setLevel(level = logging.DEBUG if debug_print else logging.INFO)
    file_logger = root_logger.addHandler(console_handler)

    if fake_serial:
        from fakeserial import Serial, FAKE_LOG
        port_name = None
        Serial.prepare(fake_serial_data = FAKE_LOG)
    else:
        from serial import Serial
        from serial.tools import list_ports
        from serial.serialutil import SerialException

        check_port(port_name)

    with Serial(port = port_name, baudrate = 115200, timeout = 1) as serial_port:
        stop = Event()

        def error_handler(error_string):
            root_logger.error('error: {}'.format(error_string))
            stop.set()

        reader = SerialReader(serial = serial_port, callback = error_handler)
        file_writer = None

        if log_to_file:
            FILE_NAME = 'serial_log.txt'

            def write_error_handler(error_string):
                reader.detach(file_writer)
                error_handler(error_string)

            file_writer = SerialFileWriter(log_file_path = FILE_NAME, callback = error_handler)
            reader.attach(file_writer)
            file_writer.start()
        else:
            reader.attach(SerialPrinter())

        reader.start()

        wait_for_any_key_to_quit()

        # tear down serial reader and file writer threads before exiting
        reader.stop()
        if file_writer:
            file_writer.stop()
