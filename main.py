#!/usr/bin/env python
import select
from sys import platform
from sys import stdout
from threading import Event
from cStringIO import StringIO
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


FAKE_LOG = StringIO(r"""
(00:08.664145) [10440] [DEVAPC] sec_post_init
(00:08.664145) [10440] [DEVAPC] platform_sec_post_init - SMC call to ATF from LK
(00:08.664145) [10440] DRAM Rank :2
(00:08.664145) [10440] DRAM Rank[0] Start = 0x40000000, Size = 0x40000000
(00:08.664145) [10440] DRAM Rank[1] Start = 0x80000000, Size = 0x1ecc0000
(00:08.664145) [10440] cmdline: "console=tty0 console=ttyMT0,921600n1 root=/dev/ram vmalloc=4"\
(00:08.664313) [10440]          "96M slub_max_order=0 slub_debug=FZPUO androidboot.hardware=m"\
(00:08.664313) [10440]          "t6755 androidboot.hardware.version=SP multisim=dsds lcm=1-ot"\
(00:08.664313) [10440]          "m1906a_fhd_dsi_vdo_6inch_innolux_drv fps=5971 vram=29229056 "\
(00:08.664313) [10440]          "bootopt=64S3,32N2,64N2 printk.disable_uart=0 ddebug_query="f"\
(00:08.664313) [10440]          "ile *mediatek* +p ; file *gpu* =_" bootprof.pl_t=1908 bootpr"\
(00:08.664313) [10440]          "of.lk_t=5278 boot_reason=0 androidboot.serialno=EP72520106 a"\
(00:08.664313) [10440]          "ndroidboot.bootreason=power_key initcall_debug=1 usb2jtag_mo"\
(00:08.664313) [10440]          "de=0 mrdump_ddrsv=yes mrdump.lk=MRDUMP04 mrdump_rsvmem=0x460"\
(00:08.664313) [10440]          "00000,0x400000,0x44800000,0xdc240,0x0,0x200000,0x448dc200,0x"\
(00:08.664313) [10440]          "364 androidboot.veritymode=enforcing androidboot.verifiedboo"\
(00:08.664313) [10440]          "tstate=green androidboot.bootloader=s1 oemandroidboot.s1boot"\
(00:08.664313) [10440]          "=1302-9781_S1_Boot_MT6755_N0.MP103_306 androidboot.serialno="\
(00:08.664536) [10440]          "EP72520106 ta_info=4,16,256 startup=0x00000001 warmboot=0x00"\
(00:08.664536) [10440]          "000000 oemandroidboot.imei=0044024557705600 oemandroidboot.p"\
(00:08.664536) [10440]          "honeid=0000:0044024557705600 oemandroidboot.security=1 oeman"\
(00:08.664536) [10440]          "droidboot.babe09a9=01 oemandroidboot.securityflags=0x0000000"\
(00:08.664536) [10440]          "2".
(00:08.664536) [10440] lk boot time = 5278 ms
(00:08.664536) [10440] lk boot mode = 0
(00:08.664536) [10440] lk boot reason = power_key
(00:08.664536) [10440] lk finished --> jump to linux kernel 64Bit
    """)


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
        from fakeserial import Serial
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
