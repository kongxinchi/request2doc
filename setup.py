#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from distutils.core import setup
import glob
import py2exe

setup(
    windows=['request2doc_gui.py'],
    data_files=[('templates', glob.glob('templates\\*.tpl'))],
    options={
        'py2exe': {
            'compressed': 1,
            'optimize': 2
        }
    }
)
