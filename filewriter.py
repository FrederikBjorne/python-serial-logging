#!/usr/bin/env python

import logging

from threading import Thread, Event
from Queue import Queue, Empty as QueueEmpty
import codecs


class FileWriter(Thread):
    '''
    This thread reads log lines from a queue and writes these to a file passed as log_file_path.
    The log line queue is filled with new log lines by calling put().
    Quits if stop() is called. Setting the read_queue_timer for reading the queue determine
    the responsiveness to stop call and is optional.
    '''
    READ_NEW_LOGLINE_TMO = 0.5
    THREAD_NAME = 'FileWriter'

    def __init__(self,
                 log_file_path,
                 callback,
                 read_queue_timeout=READ_NEW_LOGLINE_TMO,
                 name=THREAD_NAME,
                 encoding='utf8'):
        """
        :param log_file_path: The file path to write log lines to.
        :param callback: A callback method for calling back to application when error occurs.
        :param read_queue_timeout: The read timeout to avoid blocking.
        :param name: The thread name.
        :param encoding: The encoding format when writing to file.
        """
        super(FileWriter, self).__init__(name = name)
        self._read_queue_timeout = read_queue_timeout
        self._log_file_path = log_file_path
        self._encoding = encoding

        self.setDaemon(True)
        self._log_line_queue = Queue()
        self._stop = Event()
        self.logger = logging.getLogger(self.THREAD_NAME)
        self._callback = callback
        codecs.register_error('backslashreplace', self.backslash_replace)

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r})'.format(self.__class__.__name__,
                                                   self.getName(),
                                                   self._read_queue_timeout,
                                                   self._log_file_path,
                                                   self._encoding)

    def put(self, text_line):
        """
        Puts a text line to the text queue to be written to the specified file for logging.
        :param text_line: A text line to be written to file.
        """
        self._log_line_queue.put(text_line)  # Queue calls are thread-safe

    def stop(self):
        """
        Stop writing to a log file from the internal queue and commit suicide.
        """
        self._stop.set()
        self.logger.debug('writer stopped')
        if self.is_alive():
            self.join()
        self.logger.debug('writer has terminated')

    @staticmethod
    def backslash_replace(error):
        """
        An error handler to be called if escape characters are read from the log line queue input.
        """
        return u"".join([u"\\x{:x}".format(ord(error.object[i]))
                         for i in range(error.start, error.end)]), error.end

    def run(self):
        try:
            with codecs.open(self._log_file_path, 'wb', self._encoding) as log_file:
                self.logger.info('start writing to file.')

                while not self._stop.is_set():
                    try:  # timeout avoids blocking in order to be responsive to stop calls
                        log_line = self._log_line_queue.get(timeout=self._read_queue_timeout)
                    except QueueEmpty:
                        continue
                    else:
                        self._log_line_queue.task_done()
                        log_file.write(log_line + '\n')
        except Exception as e:  # this may occur if codecs fails somehow
            self.logger.error('Error: {}'.format(e))
            self._callback('{} has stopped running. error: {}'.format(self.getName(), str(e)))  # call back error

        self.logger.info('stopped writing to file.')
