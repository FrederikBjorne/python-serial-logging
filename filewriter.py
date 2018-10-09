#!/usr/bin/env python

import logging

from threading import Thread, Event
from Queue import Queue, Empty
import codecs


class FileWriter(Thread):
    '''
    This thread reads text from a queue and writes these to a file passed as log_file_path.
    The text queue is filled with new text lines by calling put().
    Quits if stop() is called. Setting the read_queue_timer for reading the queue determine
    the responsiveness to stop call and is optional.
    '''
    READ_NEW_LOGLINE_TMO = 0.5
    THREAD_NAME = 'FileWriter'

    def __init__(self,
                 log_file_path,
                 read_queue_timer=READ_NEW_LOGLINE_TMO,
                 name=THREAD_NAME,
                 encoding='utf8'):
        super(FileWriter, self).__init__(name = name)
        self._read_queue_timer = read_queue_timer
        self._log_file_path = log_file_path
        self._encoding = encoding

        self.setDaemon(True)
        self._text_queue = Queue()
        self._stop = Event()
        codecs.register_error('backslashreplace', self.backslash_replace)
        self.logger = logging.getLogger(self.THREAD_NAME)

    def put(self, text_line):
        '''
        Puts a text line to the text queue to be written to the specified file for logging.
        :param text_line: A text line to be written to file.
        '''
        self._text_queue.put(text_line)  # Queue calls are thread-safe

    def stop(self):
        '''
        Stop writing to a log file from the internal queue and commit suicide.
        '''
        self._stop.set()
        self.logger.debug('stop writer')
        self.join()

    @staticmethod
    def backslash_replace(error):
        """
        An error handler to be called when escape characters are read from the text queue input.
        """
        return u"".join([u"\\x{:x}".format(ord(error.object[i]))
                         for i in range(error.start, error.end)]), error.end

    def run(self):
        with codecs.open(self._log_file_path, 'wb', self._encoding) as log_file:
            self.logger.info('Start writing to file.')
            while not self._stop.is_set():
                try:  # timeout avoids blocking in order to be responsive to stop calls
                    log_line = self._text_queue.get(timeout=self._read_queue_timer)
                except Empty:
                    continue
                else:
                    self._text_queue.task_done()
                    log_file.write(str(log_line) + '\n')

        self.logger.info('stopped writing to file.')
