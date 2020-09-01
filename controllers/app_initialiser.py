import logging


class AppInitialiser:
    def __init__(self, args):
        self.args = args
    
    def init_app(self):
        if self.args.verbose_debug:
            verbose_level = logging.DEBUG
        else:
            verbose_level = logging.INFO # INFO is the default option
        logging.basicConfig(level=verbose_level, format='%(message)s')

        if self.args.validatecerts is None:
            logging.info("N1QLMap is executed with the default settings.")
            logging.info("[*] Certificate validation of the remote server is not enforced.")