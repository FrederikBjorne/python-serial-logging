#!/usr/bin/env python

from serial.serialutil import SerialException
from serial.tools import list_ports


class SerialPortHelper(object):
    """
    This class provides listing of serial port names and relies on pyserial's tools.
    """
    @classmethod
    def list_ports(cls):
        """
        Prints all available serial ports.
        :note: On mac osx, all ports may not be seen.
        """
        for port in list_ports.comports():
            print('{}'.format(port))

    @classmethod
    def check_port(cls, port_name):
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


if __name__ == "__main__":
    import argparse
    from os.path import basename

    # CLI
    program_name = basename(__file__)
    parser = argparse.ArgumentParser(description=('List serial ports CLI\n\n'),
                                     prog = program_name,
                                     epilog = ('\n  %(prog)s -l\n'
                                               '  %(prog)s -p COM1\n'),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--listports', help='list serial ports', action='store_true')
    group.add_argument('-p', '--port', type=str, help = 'check if a port is available')
    args = parser.parse_args()

    if args.listports:
        SerialPortHelper.list_ports()

    if args.port:
        try:
            SerialPortHelper.check_port(args.port)
            print('Port {} is avaliable.'.format(args.port))
        except SerialException as e:
            print(e)
