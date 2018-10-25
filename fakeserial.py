#!/usr/bin/env python
from __future__ import print_function  # Remove when stepping up to python 3

import logging
from StringIO import StringIO

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

# A fake log for testing purposes
FAKE_LOG = StringIO(r"""
[DEVAPC] sec_post_init
[DEVAPC] platform_sec_post_init - SMC call to ATF from LK
DRAM Rank :2
DRAM Rank[0] Start = 0x40000000, Size = 0x40000000
DRAM Rank[1] Start = 0x80000000, Size = 0x1ecc0000
 cmdline: "console=tty0 console=ttyMT0,921600n1 root=/dev/ram vmalloc=4"\
          "96M slub_max_order=0 slub_debug=FZPUO androidboot.hardware=m"\
          "t6755 androidboot.hardware.version=SP multisim=dsds lcm=1-ot"\
          "m1906a_fhd_dsi_vdo_6inch_innolux_drv fps=5971 vram=29229056 "\
          "bootopt=64S3,32N2,64N2 printk.disable_uart=0 ddebug_query="f"\
          "ile *mediatek* +p ; file *gpu* =_" bootprof.pl_t=1908 bootpr"\
          "of.lk_t=5278 boot_reason=0 androidboot.serialno=EP72520106 a"\
          "ndroidboot.bootreason=power_key initcall_debug=1 usb2jtag_mo"\
          "de=0 mrdump_ddrsv=yes mrdump.lk=MRDUMP04 mrdump_rsvmem=0x460"\
          "00000,0x400000,0x44800000,0xdc240,0x0,0x200000,0x448dc200,0x"\
          "364 androidboot.veritymode=enforcing androidboot.verifiedboo"\
          "tstate=green androidboot.bootloader=s1 oemandroidboot.s1boot"\
          "=1302-9781_S1_Boot_MT6755_N0.MP103_306 androidboot.serialno="\
          "EP72520106 ta_info=4,16,256 startup=0x00000001 warmboot=0x00"\
          "000000 oemandroidboot.imei=0044024557705600 oemandroidboot.p"\
          "honeid=0000:0044024557705600 oemandroidboot.security=1 oeman"\
          "droidboot.babe09a9=01 oemandroidboot.securityflags=0x0000000"\
          "2".
 lk boot time = 5278 ms
 lk boot mode = 0
 lk boot reason = power_key
 lk finished --> jump to linux kernel 64Bit
""")
