#!/usr/bin/env python

import logging
from datetime import datetime
from threading import Thread, Event

from observer import Observable


class SerialReader(Thread, Observable):
    '''
    This class is responsible for reading from the serial port (UART/RS-232) and update log lines
    to its registered observers.
    '''
    NAME = 'SerialReader'
    logger = logging.getLogger(NAME)

    def __init__(self, serial, do_timestamp = True, name = NAME):
        Thread.__init__(self, name = name)
        Observable.__init__(self)
        self.setDaemon(True)

        self._stop = Event()
        self._do_timestamp = do_timestamp
        self._port = serial
        self._start_time = None  # Is set when first log line arrives from serial port.

    def time_stamp(self, line):
        """
        Returns the line with a timestamp suitable for a log file.
        :param line: A read line from serial port without timestamp.
        :return: timestamp + line
        """
        time_delta = datetime.now() - self._start_time
        return '(' + ':'.join(str(time_delta).split(':')[1:]) + ') ' + line

    def stop(self):
        """
        Stop reading from the serial port and commit suicide.
        """
        self._stop.set()
        self.logger.debug('stop logging')
        self.join()

    def run(self):
        try:  # http://pyserial.readthedocs.io/en/latest/shortintro.html#readline
            first_line_received = True
            i = 0

            self.logger.info('Start reading from serial port.')
            while not self._stop.is_set():
                # we loop for every line to detect timeout, but also because it is convenient and idiomatic.
                line = self._port.readline().decode('ascii', 'backslashreplace')
                if first_line_received:
                    self._start_time = datetime.now()
                    first_line_received = False
                if line:
                    self.logger.debug('{}: {}'.format(i, line))
                    if self._do_timestamp:
                        line = self.time_stamp(line)
                    self.notify(line)
                    i += 1
        except Exception as e:
            self.logger.error('Error: {}'.format(e))
            raise  # Raise error to caller.

        self.logger.info('stopped reading from serial port.')
