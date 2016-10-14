#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Convert request parameters and response JSON to doc format
Author: Konglo
"""

import sys
import urlparse
import os
import json
import urllib2
import urllib
import cookielib
import hashlib
import re
from jinja2 import Environment

CURRENT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


class ExpandItem(object):
    def __init__(self, route, values, options=None, guess_type=False):
        self.route = route                                        # 从顶到叶子级键值的数组 e.g. ['a', 'b', 'c'...]
        self.values = values                                      # 可能的值
        self.options = [] if options is None else options        # 最子集key可能的键值
        self.guess_type = guess_type

    @staticmethod
    def guess_string_type(value):
        if type(value) == unicode or type(value) == str:
            if value.isdigit():
                return 'Int'
            elif re.search(ur'^[-+]?[0-9]+\.[0-9]+$', value):
                return 'Float'
            else:
                return 'String'
        return None

    def pretty_type_name(self, value):
        if value is None:
            return None
        elif type(value) == list:
            sub_types = []
            for sub_v in value:
                sub_type = self.pretty_type_name(sub_v)
                if sub_type is None or sub_type in sub_types: continue
                sub_types.append(sub_type)
            if len(sub_types) == 0:
                return None
            return "List<%s>" % "/".join(sub_types)
        elif type(value) == unicode or type(value) == str:
            return ExpandItem.guess_string_type(value) if self.guess_type else 'String'
        else:
            return type(value).__name__.capitalize()

    def extend_values(self, values):
        self.values.extend(values)

    def extend_options(self, options):
        self.options.extend(options)
        self.options = sorted(list(set(self.options)))

    def types(self):
        res = []
        for value in self.values:
            type_name = self.pretty_type_name(value)
            if type_name is None or type_name in res: continue
            res.append(type_name)
        return sorted(res)

    def join_slice(self, start, end, delimiter='.'):
        return delimiter.join(self.route[start: end])

    def length(self):
        return len(self.route)

    def full_key(self, delimiter='.'):
        return delimiter.join(self.route)

    def get_route_key(self, i):
        return self.route[i] if i < self.length() else None

    def set_route_key(self, i, v):
        self.route[i] = v

    def row_data(self):
        return {'name': self.full_key(), 'type': "|".join(self.types()), 'description': "|".join(self.options)}

    def __repr__(self):
        return unicode({'route': self.route, 'values': self.values, 'options': self.options})

    def __cmp__(self, other):
        if self.full_key() == other.full_key():
            return 0
        elif self.full_key() < other.full_key():
            return -1
        else:
            return 1


class DictMixer(object):
    """用于字典数据的后处理，将字典拍扁后合并同类的Key"""
    def __init__(self, data, full_key_startswith=None):
        self.__origin_data = data
        self.__expand_item_list = None
        self.__max_depth = None
        self.delimiter = '.'
        self.symbol = '*'
        self.full_key_startswith = full_key_startswith
        self.route_startswith = full_key_startswith.split('.') if full_key_startswith else []

    @staticmethod
    def is_leaf_item(item):
        if type(item) == list:
            for sub in item:
                if type(sub) == dict or type(sub) == list:
                    return False
        elif type(item) == dict:
            return False
        return True

    def expand_item_recursive(self, route, item):
        """递归获取ExpandItem"""
        if self.full_key_startswith and not self.full_key_startswith.startswith('.'.join(route[0: len(self.route_startswith)])):
            return []

        result = []
        if self.is_leaf_item(item):
            result.append(ExpandItem(route[len(self.route_startswith):], [item]))
        elif type(item) == list:
            for i, sub_item in enumerate(item):
                sub_route = route + [unicode(i)]
                result.extend(self.expand_item_recursive(sub_route, sub_item))
        elif type(item) == dict:
            for k, sub_item in item.items():
                sub_route = route + [unicode(k)]
                result.extend(self.expand_item_recursive(sub_route, sub_item))
        return result

    def expand_item_list(self):
        """
        将有多级的dict平铺 e.g. {'k1':{'k2':{'k3':1}}} => {'route': ['k1','k2','k3'], 'values':[1]}
        :return: dict
        """
        if self.__expand_item_list is None:
            self.__expand_item_list = self.expand_item_recursive([], self.__origin_data)
        return self.__expand_item_list

    def max_depth(self):
        if self.__max_depth is None:
            depth = 0
            for item in self.expand_item_list():
                if len(item.route) > depth:
                    depth = len(item.route)
            self.__max_depth = depth
        return self.__max_depth

    @staticmethod
    def children_summary_key(current_index, children):
        """用于判断一个prefix和另一个prefix是否可以合并的唯一标识"""
        keys = [item.join_slice(0, current_index)+"."+item.get_route_key(current_index+1) for item in children]
        keys = list(set(keys))
        return hashlib.md5("_".join(keys)).hexdigest()

    def find_children_by_prefix(self, prefix):
        """查某个前缀开头的item集合"""
        res = []
        for item in self.expand_item_list():
            if item.full_key(self.delimiter).startswith(prefix+self.delimiter):
                res.append(item)
        return res

    def find_unique_prefix_list(self, current_index):
        """获取每个item的[0:current_index+1]的route，拼接成字符串，并去重"""
        prefix_list = []
        for item in self.expand_item_list():
            if item.length() <= current_index: continue
            prefix_list.append(item.join_slice(0, current_index+1, self.delimiter))
        return list(set(prefix_list))

    def replace_similar_items_route(self):
        """将各个item中相似的键值替换为*"""
        i = 1
        while i < self.max_depth():
            prefix_children = {}
            summary_key_prefix_list = {}
            prefix_list = self.find_unique_prefix_list(i)
            for prefix in prefix_list:
                children = self.find_children_by_prefix(prefix)
                if len(children) == 0: continue

                prefix_children[prefix] = children

                similar_key = self.children_summary_key(i, children)
                if not summary_key_prefix_list.has_key(similar_key):
                    summary_key_prefix_list[similar_key] = []
                summary_key_prefix_list[similar_key].append(prefix)

            for prefix_list in summary_key_prefix_list.values():
                if len(prefix_list) > 1:
                    options = []
                    for prefix in prefix_list:
                        for item in prefix_children[prefix]:
                            item.set_route_key(i, self.symbol)
                        options.append(prefix.split(self.delimiter)[-1])

                    self.__expand_item_list.append(
                        ExpandItem(
                            prefix_list[0].split(self.delimiter)[0:-1] + [self.symbol],
                            [],
                            options
                        )
                    )
            i += 1

    def merge_items(self):
        """将full_key相同的项合并"""
        dic = {}
        for item in self.expand_item_list():
            key = item.full_key()
            if not dic.has_key(key):
                dic[key] = ExpandItem(item.route[:], [], item.options[:])
            dic[key].extend_values(item.values)
            dic[key].extend_options(item.options)
        self.__expand_item_list = sorted(dic.values())


class Request2Doc(object):
    def __init__(self, url='', method='', forms=None):
        self.url = url
        self.method = method
        self.forms = forms if type(forms) == dict else {}
        self.response_body = None
        self.response_data = None
        self.parse = json.loads
        self.slice_startswith = None
        self.cookie = None
        self.headers = []
        self.errors = []

    def args(self):
        parsed = urlparse.urlparse(self.url)
        return {k: v[0] for k, v in urlparse.parse_qs(parsed.query).items()}

    def set_slice_startswith(self, slice_startswith):
        self.slice_startswith = slice_startswith

    def set_cookie_jar(self, cookie_jar_path):
        self.cookie = cookielib.MozillaCookieJar()
        self.cookie.load(cookie_jar_path, ignore_discard=True, ignore_expires=True)

    def set_headers(self, headers):
        for header in headers:
            parts = header.split(':')
            if len(parts) != 2: continue
            self.headers.append(
                (parts[0].strip(), parts[1].strip())
            )

    def validate(self):
        self.errors = []
        if not self.url:
            self.errors.append({'message': u'URL is Empty'})
        else:
            parsed = urlparse.urlparse(self.url)
            if not (parsed.scheme in ['http', 'https'] and parsed.netloc):
                self.errors.append({'message': u'URL is illegal'})
        if not self.method:
            self.errors.append({'message': u'Method is Empty'})
        return len(self.errors) == 0

    def error_message(self):
        return '\n'.join([e['message'] for e in self.errors])

    def request(self):
        """发送请求"""
        req_data = urllib.urlencode(self.forms) if self.forms else None
        request = urllib2.Request(self.url, req_data)
        request.get_method = lambda: self.method

        # 添加头
        for header_key, header_value in self.headers:
            request.add_header(header_key, header_value)

        # 添加cookie-jar
        if self.cookie is not None:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        else:
            opener = urllib2.build_opener()

        res = opener.open(request)
        self.response_body = res.read()
        return True

    def set_response_body(self, body):
        self.response_body = body

    def get_response_data(self):
        """解析请求返回的数据"""
        if not self.response_data:
            self.response_data = self.parse(self.response_body)
        return self.response_data

    def render_string(self, tpl_path):
        """渲染数据，输出为字符串"""
        request_get_dict = self.args()
        request_post_dict = self.forms

        # 处理接口返回的数据为可展示的形式
        mixer = DictMixer(self.get_response_data(), self.slice_startswith)
        mixer.replace_similar_items_route()
        mixer.merge_items()

        return Environment()\
            .from_string(open(tpl_path, 'rb').read().decode('utf-8'))\
            .render(url=self.url.split('?')[0],
                    method=self.method,
                    request_get_items=[ExpandItem([k], [v], None, True).row_data() for k, v in request_get_dict.items()],
                    request_post_items=[ExpandItem([k], [v], None, True).row_data() for k, v in request_post_dict.items()],
                    response_items=[item.row_data() for item in mixer.expand_item_list()],
                    response_body=json.dumps(self.get_response_data(), ensure_ascii=False, indent=2))

    def render_save_as(self, tpl_path, output_path):
        """渲染数据，并保存到指定路径"""
        content = self.render_string(tpl_path)
        with open(output_path, 'wb') as f:
            f.write(content.encode('utf-8'))


def build_request2doc_handler(url, method, request_forms_data="", headers=[], cookie_jar=None, slice_startswith=None):
    request_forms = {k: v[0] for k, v in urlparse.parse_qs(request_forms_data).items()}

    handler = Request2Doc(url, method, request_forms)
    if slice_startswith:
        handler.set_slice_startswith(slice_startswith)
    if cookie_jar:
        handler.set_cookie_jar(cookie_jar)
    if headers:
        handler.set_headers(headers)
    return handler


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?', action='store', default='', help=u'URL')
    parser.add_argument('-d', '--data', nargs='?', action='store', default="", help=u'POST数据键值对, e.g. key1=value&key2=value')
    parser.add_argument('-t', '--template', nargs='?', action='store', default=os.path.join(CURRENT_DIR, 'templates', 'markup.tpl'), help=u'模板文件路径，默认为markup.tpl')
    parser.add_argument('-o', '--output', nargs='?', action='store', help=u'将文件输出到指定文件，默认为打印到屏幕')
    parser.add_argument('-s', '--slice-startswith', nargs='?', action='store', help=u'只打印返回数据中指定域的数据, e.g. data.results')
    parser.add_argument('-b', '--cookie-jar', nargs='?', action='store', help=u'cookie-jar文件路径')
    parser.add_argument('-H', '--header', nargs='?', action='append', help=u'自定义的附加请求头')
    args = parser.parse_args()

    request_forms = {k: v[0] for k, v in urlparse.parse_qs(args.data).items()}
    method = 'POST' if args.data else 'GET'

    handler = Request2Doc(args.url, method, request_forms)
    if args.slice_startswith:
        handler.set_slice_startswith(args.slice_startswith)
    if args.cookie_jar:
        handler.set_cookie_jar(args.cookie_jar)
    if args.header:
        handler.set_headers(args.header)

    if not handler.request():
        pass

    if args.output:
        handler.render_save_as(args.template, args.output)
    else:
        print handler.render_string(args.template)

if __name__ == '__main__':
    exit(main())
