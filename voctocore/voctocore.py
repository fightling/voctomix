#!/usr/bin/env python3
import gi
import signal
import logging
import sys

# import GStreamer and GLib-Helper classes
gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
from gi.repository import Gst, GObject

# import local classes
from lib.loghandler import LogHandler

# check min-version
minGst = (1, 5)
minPy = (3, 0)

Gst.init([])
if Gst.version() < minGst:
    raise Exception('GStreamer version', Gst.version(),
                    'is too old, at least', minGst, 'is required')

if sys.version_info < minPy:
    raise Exception('Python version', sys.version_info,
                    'is too old, at least', minPy, 'is required')


# init GObject & Co. before importing local classes
GObject.threads_init()


# main class
class Voctocore(object):

    def __init__(self):
        # import local which use the config or the logging system
        # this is required, so that we can configure logging,
        # before reading the config
        from lib.pipeline import Pipeline
        from lib.controlserver import ControlServer

        self.log = logging.getLogger('Voctocore')
        self.log.debug('creating GObject-MainLoop')
        self.mainloop = GObject.MainLoop()

        # initialize subsystem
        self.log.debug('creating A/V-Pipeline')
        self.pipeline = Pipeline()

        self.log.debug('creating ControlServer')
        self.controlserver = ControlServer(self.pipeline)

    def run(self):
        self.log.info('running GObject-MainLoop')
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.log.info('Terminated via Ctrl-C')

    def quit(self):
        self.log.info('quitting GObject-MainLoop')
        self.mainloop.quit()


# run mainclass
def main():
    # parse command-line args
    from lib import args
    args.parse()

    from lib.args import Args
    docolor = (Args.color == 'always') or (Args.color == 'auto' and
                                           sys.stderr.isatty())

    handler = LogHandler(docolor, Args.timestamp)
    logging.root.addHandler(handler)

    if Args.verbose >= 2:
        level = logging.DEBUG
    elif Args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.root.setLevel(level)

    # make killable by ctrl-c
    logging.debug('setting SIGINT handler')
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logging.info('Python Version: %s', sys.version_info)
    logging.info('GStreamer Version: %s', Gst.version())

    logging.debug('loading Config')
    from lib import config
    config.load()

    # init main-class and main-loop
    logging.debug('initializing Voctocore')
    voctocore = Voctocore()

    logging.debug('running Voctocore')
    voctocore.run()


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as e:
        logging.error(str(e))
        sys.exit(1)
