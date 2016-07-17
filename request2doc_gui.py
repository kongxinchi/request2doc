#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
request2doc GUI
Author: xinchi.kong
"""

import wx
from request2doc import *

TEMPLATES_DIR = os.path.join(CURRENT_DIR, 'templates')


class InputPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # URL输入框
        self.url_text = wx.TextCtrl(self, -1)
        url_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "URL"))
        url_sizer.Add(self.url_text, 1, wx.EXPAND)

        # 请求方式与参数
        self.method_choice = wx.Choice(self, -1, size=(100, -1), choices=[u'GET', u'POST'])
        self.method_choice.SetSelection(0)
        self.params_text = wx.TextCtrl(self, -1, size=(-1, 50), style=wx.TE_MULTILINE)
        params_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Params"), wx.VERTICAL)
        params_sizer.Add(self.method_choice, 0)
        params_sizer.Add(self.params_text, 1, wx.EXPAND | wx.TOP, 5)

        # 请求头
        self.headers_text = wx.TextCtrl(self, -1, size=(-1, 50), style=wx.TE_MULTILINE)
        headers_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Headers"))
        headers_sizer.Add(self.headers_text, 1, wx.EXPAND)

        # 输出模板
        self.template_choice = wx.Choice(self, -1, size=(150, -1), choices=[])
        template_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Template"))
        template_sizer.Add(self.template_choice, 1, wx.EXPAND)

        # 返回数据中的域指定
        self.slice_text = wx.TextCtrl(self, -1)
        slice_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Response slice startswith"))
        slice_sizer.Add(self.slice_text, 1, wx.EXPAND)

        # 按钮
        transform_button = wx.Button(self, -1, u'Only Transform', size=(130, 30))
        request_transform_button = wx.Button(self, -1, u'Request And Transform', size=(170, 30))
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add((0, 0), 1)
        button_sizer.Add(transform_button, 0)
        button_sizer.Add(request_transform_button, 0)

        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(url_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(params_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(headers_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(template_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(slice_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.SetSizer(main_box)

        self.preload_templates()

    def preload_templates(self):
        names = []
        for f in os.listdir(TEMPLATES_DIR):
            if os.path.isfile(os.path.join(TEMPLATES_DIR, f)) and f.endswith('.tpl'):
                names.append(f[:-4])

        self.template_choice.SetItems(names)
        self.template_choice.SetSelection(0)


class OutputPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # 响应体内容
        self.response_text = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        response_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Response"))
        response_sizer.Add(self.response_text, 1, wx.EXPAND)

        # 输出的文档内容
        self.doc_text = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        doc_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Document"))
        doc_sizer.Add(self.doc_text, 1, wx.EXPAND)

        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(response_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        main_box.Add(doc_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.SetSizer(main_box)


class Request2DocFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, u'Request To Document GUI', size=(1000, 500))

        main_box = wx.BoxSizer(wx.HORIZONTAL)
        input_panel = InputPanel(self)
        output_panel = OutputPanel(self)

        main_box.Add(input_panel, 4, wx.EXPAND | wx.ALL, 5)
        main_box.Add(output_panel, 6, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_box)
        self.SetAutoLayout(True)
        self.Centre()
        self.Show()

if __name__ == '__main__':
    app = wx.App()
    Request2DocFrame()
    app.MainLoop()
