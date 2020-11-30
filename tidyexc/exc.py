#!/usr/bin/env python3

import textwrap
from dotmap import DotMap
from shutil import get_terminal_size
from contextlib import contextmanager
from collections import ChainMap
from .utils import list_iadd, property_iadd, eval_template

_info_stack = []

class Error(Exception):

    @classmethod
    @contextmanager
    def add_info(cls, message, **kwargs):
        try:
            cls.push_info(message, **kwargs)
            yield
        finally:
            cls.pop_info()

    @classmethod
    def push_info(cls, message, **kwargs):
        _info_stack.append((cls, message, kwargs))

    @classmethod
    def pop_info(cls):
        for i, (cls_i, _, _) in reversed(list(enumerate(_info_stack))):
            if cls_i is cls:
                del _info_stack[i]
                return
        raise IndexError(f"no info to pop for {cls}")

    @classmethod
    def clear_info(cls):
        global _info_stack
        _info_stack = [x for x in _info_stack if x[0] is not cls]


    def __init__(self, brief, **kwargs):
        info_stack = [
                (msg, kwargs)
                for cls, msg, kwargs in _info_stack
                if isinstance(self, cls)
        ]
        info_messages, info_kwargs = \
                zip(*info_stack) if info_stack else ([], [])

        self.brief = brief
        self._info = list_iadd(info_messages)
        self._blame = list_iadd()
        self._hints = list_iadd()
        self._data = DotMap(ChainMap(kwargs, *reversed(info_kwargs)))

    @property
    def brief_str(self):
        return eval_template(self.brief, self.data)

    @property_iadd
    def info(self):
        return self._info

    @property
    def info_strs(self):
        return [eval_template(x, self.data) for x in self.info]

    @property_iadd
    def blame(self):
        return self._blame

    @property
    def blame_strs(self):
        return [eval_template(x, self.data) for x in self.blame]

    @property_iadd
    def hints(self):
        return self._hints

    @property
    def hint_strs(self):
        return [eval_template(x, self.data) for x in self.hints]

    @property
    def data(self):
        return self._data

    def __str__(self):
        message = ""
        parts = [
                ('',  [self.brief_str]),
                ('• ', self.info_strs),
                ('✖ ', self.blame_strs),
                ('• ', self.hint_strs),
        ]
        w = get_terminal_size().columns

        for bullet, strs in parts:
            b = len(bullet)

            for s in strs:
                s = textwrap.fill(s, width=w-b)
                s = textwrap.indent(s, b*' ')
                s = bullet + s[b:]
                message += s + '\n'

        return message
