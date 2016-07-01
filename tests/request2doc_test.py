#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import unittest
import sys
import json
sys.path.append('../')
from request2doc import DictMixer, Request2Doc


class Request2DocTestCase(unittest.TestCase):

    def test_request2doc(self):
        md = Request2Doc('http://zxlocal.test.17zuoye.net/teacher/homework/search', 'GET', {'status': 0})
        md.set_cookie_jar('D:\\coding\\request2doc\\cookiejar')
        print md.request()
        print md.response_body
        print md.render_string('../markup.tpl')

if __name__ == '__main__':
    unittest.main()
