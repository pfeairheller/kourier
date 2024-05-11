# -*- encoding: utf-8 -*-
"""
KERI
kourier.app.cli.commands module

healthKERI REST API Service
"""
import argparse
import logging

from kourier.app import mailing
from keri import __version__
from keri import help
from keri.app import directing

parser = argparse.ArgumentParser(description="This is the bar command")
parser.set_defaults(handler=lambda args: launch(args))
parser.add_argument('-V', '--version',
                    action='version',
                    version=__version__,
                    help="Prints out version of script runner.")
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('-H', '--http',
                    action='store',
                    default=9632,
                    help="Local port number the HTTP server listens on. Default is 7632.")
parser.add_argument('-o', '--host',
                    action='store',
                    default="127.0.0.1",
                    help="Local host IP address HTTP server listens on. Default is 127.0.0.1.")
parser.add_argument('--bootport', '-bp',
                    action='store',
                    default=9631,
                    help="Local port number the HTTP server listens on. Default is 7631.")
parser.add_argument('--boothost', '-bh',
                    action='store',
                    default="127.0.0.1",
                    help="Local host IP address HTTP server listens on. Default is 127.0.0.1.")
parser.add_argument("--config-dir", "-c", dest="configDir", help="directory override for configuration data")
parser.add_argument('--config-file',
                    dest="configFile",
                    action='store',
                    default=None,
                    help="configuration filename override")
parser.add_argument("--loglevel", action="store", required=False, default="INFO",
                    help="Set log level to DEBUG | INFO | WARNING | ERROR | CRITICAL. Default is INFO")
parser.add_argument("--logfile", action="store", required=False, default=None,
                    help="path of the log file. If not defined, logs will not be written to the file.")
parser.add_argument("--keypath", action="store", required=False, default=None)
parser.add_argument("--certpath", action="store", required=False, default=None)
parser.add_argument("--cafilepath", action="store", required=False, default=None)

FORMAT = '%(asctime)s [kourier] %(levelname)-8s %(message)s'


def launch(args):
    help.ogler.level = logging.getLevelName(args.loglevel)
    baseFormatter = logging.Formatter(FORMAT)  # basic format
    baseFormatter.default_msec_format = None
    help.ogler.baseConsoleHandler.setFormatter(baseFormatter)
    help.ogler.level = logging.getLevelName(args.loglevel)

    if args.logfile is not None:
        help.ogler.headDirPath = args.logfile
        help.ogler.reopen(name="kourier", temp=False, clear=True)

    logger = help.ogler.getLogger()

    logger.info("******* Starting KERI Inbox as a Service: http/%s"
                ".******", args.http)

    runService(args)

    logger.info("******* Ended KERI Inbox as a Service: http/%s"
                ".******", args.http)


def runService(args, expire=0.0):
    """
    Setup and run one witness
    """

    doers = mailing.setup(base=args.base,
                          host=args.host,
                          port=int(args.http),
                          bootHost=args.boothost,
                          bootPort=int(args.bootport),
                          keypath=args.keypath,
                          certpath=args.certpath,
                          cafilepath=args.cafilepath)

    directing.runController(doers=doers, expire=expire)
