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
import hashlib
from jinja2 import Environment

CURRENT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


class ExpandItem(object):
    def __init__(self, route, values, options=None):
        self.route = route                                                 # 从顶到叶子级键值的数组 e.g. ['a', 'b', 'c'...]
        self.values = values                                               # 可能的值
        self.options = [] if options is None else options        # 最子集key可能的键值

    def types(self):
        res = [unicode(type(v)) for v in self.values]
        return list(set(res))

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
        return {'name': self.full_key(), 'type': "/".join(self.types()), 'description': "/".join(self.options)}

    def __repr__(self):
        return unicode({'route': self.route, 'values': self.values, 'options': self.options})


class DictMixer(object):
    """用于字典数据的后处理，将字典拍扁后合并同类的Key"""
    def __init__(self, data):
        self.__origin_data = data
        self.__expand_item_list = None
        self.__max_depth = None
        self.delimiter = '.'
        self.symbol = 'x'

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
        result = []
        if self.is_leaf_item(item):
            result.append(ExpandItem(route, [item]))
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
                        for chd_index, item in enumerate(prefix_children[prefix]):
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
            dic[key].values.extend(item.values)
        self.__expand_item_list = sorted(dic.values())


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

    def render_string(self, tpl_path):
        request_get_dict = self.args
        request_post_dict = self.forms

        mixer = DictMixer(self.get_response_data())
        mixer.replace_similar_items_route()
        mixer.merge_items()

        return Environment()\
            .from_string(open(tpl_path, 'rb').read().decode('utf-8'))\
            .render(url=self.url,
                    method=self.method,
                    request_get_dict=request_get_dict,
                    request_post_dict=request_post_dict,
                    response_item_list=[item.row_data() for item in mixer.expand_item_list()],
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