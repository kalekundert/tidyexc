#!/usr/bin/env python3

import textwrap
from dotmap import DotMap
from shutil import get_terminal_size
from contextlib import contextmanager
from collections import ChainMap

_info_stack = []

class Error:

    def __init__(self, brief, **kwargs):
        if _info_stack:
            info_messages, info_data = zip(*_info_stack)
        else:
            info_messages, info_data = [], []

        self.brief = brief
        self.info = MessageList(info_messages)
        self.blame = MessageList()
        self.hints = MessageList()
        self.data = DotMap(ChainMap(kwargs, *reversed(info_data)))

    @property
    def brief_str(self):
        return eval_template(self.brief, self.data)

    @property
    def info_strs(self):
        return [eval_template(x, self.data) for x in self.info]

    @property
    def blame_strs(self):
        return [eval_template(x, self.data) for x in self.blame]

    @property
    def hint_strs(self):
        return [eval_template(x, self.data) for x in self.hints]

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

class MessageList(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iadd__(self, message):
        self.append(message)
        return self

@contextmanager
def info(message, **kwargs):
    try:
        push_info(message, **kwargs)
        yield
    finally:
        pop_info()

def push_info(message, **kwargs):
    _info_stack.append((message, kwargs))

def pop_info():
    _info_stack.pop()

def clear_info():
    _info_stack = []

def eval_template(template, data):
    if callable(template):
        return template(data)
    else:
        return template.format(**data)

