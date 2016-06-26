#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Convert request parameters and response JSON to doc format
Author: xinchi.kong
"""

import sys
import urlparse
import os
import json
import urllib2
import urllib
from jinja2 import Environment

CURRENT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


class SumDict(dict):

    def __init__(self, seq=None, **kwargs):
        super(SumDict, self).__init__(seq, **kwargs)
        self.unique_key = ','.join([unicode(k) for k in self.keys()])

    def expand_dict_recursive(self, prefix, item):
        result = {}
        if type(item) == list:
            for i, sub_item in enumerate(item):
                sub_prefix = "%s.%d" % (prefix, i) if prefix else "%d" % i
                result.update(self.expand_dict_recursive(sub_prefix, sub_item))
        elif type(item) == dict or type(item) == SumDict:
            for k, sub_item in item.items():
                sub_prefix = "%s.%s" % (prefix, k) if prefix else "%s" % k
                result.update(self.expand_dict_recursive(sub_prefix, sub_item))
        else:
            result[prefix] = item
        return result

    def expand_dict(self):
        return self.expand_dict_recursive("", self)


class Request2Doc(object):
    def __init__(self, url, method, args=None, forms=None):
        self.url = url
        self.method = method
        self.args = args if type(args) == dict else {}
        self.forms = forms if type(forms) == dict else {}
        self.response_body = None
        self.response_data = None
        self.parse = json.loads

    def request(self):
        url = self.url + '?' + urllib.urlencode(self.args)
        req_data = urllib.urlencode(self.forms) if self.forms else None
        request = urllib2.Request(url, req_data)
        request.get_method = lambda: self.method
        res = urllib2.urlopen(request)
        self.response_body = res.read()
        return True

    def get_response_data(self):
        if not self.response_data:
            self.response_data = self.parse(self.response_body)
        return self.response_data

    def response_sum_dict(self):
        return SumDict(self.get_response_data())

    def render_string(self, tpl_path):
        request_get_dict = self.args
        request_post_dict = self.forms

        return Environment()\
            .from_string(open(tpl_path, 'rb').read().decode('utf-8'))\
            .render(url=self.url,
                    method=self.method,
                    request_get_dict=request_get_dict,
                    request_post_dict=request_post_dict,
                    response_dict=self.response_sum_dict().expand_dict(),
                    response_body=json.dumps(self.get_response_data(), indent=2))

    def render_save_as(self, tpl_path, output_path):
        content = self.render_string(tpl_path)
        with open(output_path, 'wb') as f:
            f.write(content.encode('utf-8'))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?', action='store', default='', help=u'URL')
    parser.add_argument('-d', '--data', nargs='?', action='store', default="", help=u'POST data, e.g. key1=value&key2=value')
    parser.add_argument('-t', '--template', nargs='?', action='store', default=os.path.join(CURRENT_DIR, 'markup.tpl'), help=u'Template file path')
    parser.add_argument('-o', '--output', nargs='?', action='store', help=u'Output file path')
    args = parser.parse_args()

    parsed = urlparse.urlparse(args.url)
    url = "%s://%s%s" % (parsed.scheme, parsed.netloc, parsed.path)
    request_args = {k: v[0] for k, v in urlparse.parse_qs(parsed.query).items()}
    request_forms = {k: v[0] for k, v in urlparse.parse_qs(args.data).items()}
    method = 'POST' if args.data else 'GET'

    handler = Request2Doc(url, method, request_args, request_forms)
    if not handler.request():
        # TODO
        pass

    if args.output:
        handler.render_save_as(args.template, args.output)
    else:
        print handler.render_string(args.template)

if __name__ == '__main__':
    # exit(main())
    md = Request2Doc('http://zxlocal.test.17zuoye.net/teacher/homework/search', 'GET', {'status': 0})
    print md.request()
    print md.response_body
    print md.render_string('markup.tpl')