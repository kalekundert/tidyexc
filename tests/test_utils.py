#!/usr/bin/env python3

from tidyexc import utils

def test_list_iadd():
    l = utils.list_iadd()

    l += "a"
    l += int
    l += ["c", "d"]

    assert l == ["a", int, "c", "d"]

def test_dict_attr():
    d = utils.dict_attr(a=1)

    assert d['a'] == 1
    assert d.a == 1

    d.b = 2

    assert d['b'] == 2
    assert d.b == 2

    d.c = {'d': 1}

    assert d['c'] == {'d': 1}
    assert d.c == {'d': 1}


