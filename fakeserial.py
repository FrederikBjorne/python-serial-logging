#!/usr/bin/env python
from __future__ import print_function  # Remove when stepping up to python 3

import logging

from serial.serialutil import SerialBase, SerialException, portNotOpenError


class Serial(SerialBase):
    """
       Fake Serial port implementation useful for development in cases you want to run tests
       without hardware, but also for fault injection.
    """

    _fake_serial_data = None
    logger = logging.getLogger('FakeSerial')

    @classmethod
    def prepare(cls, fake_serial_data=None):
        """
        Only for injecting fake I/O text data for testing purposes.
        :param fake_serial_data: Fake serial logging data for testing purposes.
        :type cStringIO.StringIO
        """

        Serial._fake_serial_data = fake_serial_data

    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read."""
        if not self.isOpen:
            raise portNotOpenError
        data = Serial._fake_serial_data.read(size)
        return bytes(data)

    def readline(self):
        if not self.isOpen:
            raise portNotOpenError
        data = Serial._fake_serial_data.readline()  # timeout can be ignored with StringIO text
        return str(bytes(data))

    def write(self, data):
        """Output the given string over the serial port. Can block if the
        connection is blocked. May raise SerialException if the connection is
        closed."""
        if not self.isOpen:
            raise portNotOpenError
        # nothing done
        return len(data)

    def open(self):
        """Open port with current settings. This may throw a SerialException
           if the port cannot be opened."""
        self.logger = None
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        # not that there anything to configure...
        self._reconfigurePort()
        # all things set up get, now a clean start
        self.is_open = True

    def close(self):
        """Close port"""
        if self.is_open:
            self.is_open = False

    def _reconfigurePort(self):
        """Set communication parameters on opened port. for the test://
        protocol all settings are ignored!"""
        if self.logger:
            self.logger.info('ignored port configuration change')

    def makeDeviceName(self, port):
        raise SerialException("there is no sensible way to turn numbers into URLs")

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def inWaiting(self):
        """Return the number of characters currently in the input buffer."""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            # set this one to debug as the function could be called often...
            self.logger.debug('WARNING: inWaiting returns dummy value')
        return 0 # hmmm, see comment in read()

    def flushInput(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored flushInput')

    def flushOutput(self):
        """Clear output buffer, aborting the current output and
        discarding all that is in the buffer."""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored flushOutput')

    def sendBreak(self, duration=0.25):
        """Send break condition. Timed, returns to idle state after given
        duration."""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored sendBreak({!r})'.format(duration))

    def setBreak(self, level=True):
        """Set break: Controls TXD. When active, to transmitting is
        possible."""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored setBreak({!r})'.format(level))

    def setRTS(self, level=True):
        """Set terminal status line: Request To Send"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored setRTS({!r})'.format(level))

    def setDTR(self, level=True):
        """Set terminal status line: Data Terminal Ready"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('ignored setDTR({!r})'.format(level))

    def getCTS(self):
        """Read terminal status line: Clear To Send"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for getCTS()')
        return True

    def getDSR(self):
        """Read terminal status line: Data Set Ready"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for getDSR()')
        return True

    def getRI(self):
        """Read terminal status line: Ring Indicator"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for getRI()')
        return False

    def getCD(self):
        """Read terminal status line: Carrier Detect"""
        if not self.isOpen: raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for getCD()')
        return True

    # - - - platform specific - - -
    # None so far


# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
