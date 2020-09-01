import argparse


class ArgumentParser:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("host", help="Host used to send an HTTP request e.g. https://vulndomain.net", type=str)
        parser.add_argument("-r", "--request", help="Path to an HTTP request"),
        parser.add_argument("-k", "--keyword", help="Keyword that exists in HTTP response when query is successful", type=str)
        parser.add_argument("--proxy", help="Proxy server address", type=str)
        parser.add_argument("--validatecerts", help="Set the flag to enforce certificate validation. Certificates are not validated by default!", action="store_true")

        group_verbose = parser.add_mutually_exclusive_group(required=False)
        group_verbose.add_argument("-v", "--verbose_debug", help="Set the verbosity level to debug", action="store_true")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-d", "--datastores", help="Lists available datastores", action="store_true")
        group.add_argument("-ks", "--keyspaces", help="Lists available keyspaces for specific datastore URL", type=str, metavar=('DATASTORE_URL'))
        group.add_argument("-e", "--extract", help="Extracts data from a specific keyspace", type=str, metavar=('KEYSPACE_ID'))
        group.add_argument("-q", "--query", help="Run arbitrary N1QL query", type=str)
        group.add_argument("-c", "--curl", help="Runs CURL N1QL function inside the query, can be used to SSRF", type=str, nargs='*', metavar=('ENDPOINT', 'OPTIONS'))

        self.parser = parser
    
    def parse(self):
        self.args = self.parser.parse_args()
        return self.args