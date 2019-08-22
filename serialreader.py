#!/usr/bin/env python
import codecs
import logging
from datetime import datetime
from threading import Thread, Event
from time import sleep

from observer import Observable


class SerialReader(Thread, Observable):
    """
    This class is responsible for reading from the serial port and update log lines to its
    registered observers. Thread quits if stop() is called. If an exception is raised when
    reading from serial due to I/O issues or escape characters received, this thread will
    callback to its owner to stop operation. Each log line is timestamped as default.
    """

    def __init__(self, serial, callback, do_timestamp = True):
        """
        :param serial: A Serial object for communicating with a serial port. It needs to have
                       a read timeout set. Otherwise, this class object might hang forever if
                       a end line character is never received.
                       http://pyserial.readthedocs.io/en/latest/shortintro.html#readline
        :type Serial
        :param callback: A callback method for calling back to owner when error occurs.
        :param do_timestamp: Add a timestamp to each line intercepted from the serial port.
        """
        Thread.__init__(self, name = self.__class__.__name__)
        Observable.__init__(self)
        self.setDaemon(True)

        self._stop = Event()
        self._do_timestamp = do_timestamp
        self._port = serial
        self.logger = logging.getLogger(self.__class__.__name__)
        self._start_time = None  # Is set when first log line arrives from serial port.
        self._callback = callback
        codecs.register_error('backslashreplace', self.backslash_replace)

    @staticmethod
    def backslash_replace(error):
        """
        An error handler to be called when escape characters are read from the log line queue input.
        """
        return u"".join([u"\\x{:x}".format(ord(error.object[i]))
                         for i in range(error.start, error.end)]), error.end

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r}, {!r})'.format(self.__class__.__name__,
                                                         self.getName(),
                                                         self.is_alive(),
                                                         self._do_timestamp,
                                                         self._port,
                                                         self._start_time)

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
        self.logger.debug('stop reading from serial port')
        if self.is_alive():
            self.join()
        self.logger.info('reader has terminated')

    def run(self):
        try:
            first_line_received = True
            i = 0

            self.logger.info('Start reading from serial port.')
            while not self._stop.is_set():
                # we loop for every line and if no endline is found, then read timeout will occur.
                line = self._port.readline().decode('ascii', 'backslashreplace').strip()
                sleep(0.1)  # let in other threads

                if first_line_received:
                    self._start_time = datetime.now()
                    first_line_received = False
                if line:
                    self.logger.debug('{}: {}'.format(i, line))
                    if self._do_timestamp:
                        line = self.time_stamp(line)
                    self.notify(line)  # update listeners
                    i += 1
        except Exception as e:  # this may occur if readline() fails handling an escape character
            self.logger.error('Error: {}'.format(e))
            self._callback('{} has stopped running. error: {}'.format(self.getName(), e))

        self.logger.info('stopped reading from serial port.')
