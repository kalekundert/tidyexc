#!/usr/bin/env python3

import pytest
from tidyexc.views import *

def test_data_view():
    d = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
    v = data_view(d)

    assert repr(v) == "data_view([{'a': 1, 'b': 2}, {'b': 3, 'c': 4}])"
    assert v == {'a': 1, 'b': 3, 'c': 4}
    assert len(v) == 3
    assert set(v) == {'a', 'b', 'c'}

    assert 'a' in v
    assert 'd' not in v

def test_data_view_get_set_del():
    d = [{'a': 1}, {'b': 2}]
    v = data_view(d)

    assert v.a == v['a'] == 1
    assert v.b == v['b'] == 2

    with pytest.raises(AttributeError):
        v.z
    with pytest.raises(KeyError):
        v['z']

    # attribute syntax
    v.a = 3
    v.b = 4

    assert v.a == v['a'] == 3
    assert v.b == v['b'] == 4
    assert d == [{'a': 1}, {'a': 3, 'b': 4}]

    del v.a
    del v.b

    with pytest.raises(AttributeError):
        del v.z

    assert v.a == v['a'] == 1
    assert d == [{'a': 1}, {}]

    with pytest.raises(AttributeError):
        del v.a
    with pytest.raises(AttributeError):
        del v.b
    
    # item syntax
    v['a'] = 3
    v['b'] = 4

    assert v.a == v['a'] == 3
    assert v.b == v['b'] == 4
    assert d == [{'a': 1}, {'a': 3, 'b': 4}]

    del v['a']
    del v['b']

    with pytest.raises(KeyError):
        del v['z']

    assert v.a == v['a'] == 1
    assert d == [{'a': 1}, {}]

    with pytest.raises(KeyError):
        del v['a']
    with pytest.raises(KeyError):
        del v['b']

def test_nested_data_view():
    d = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
    v = nested_data_view(d)

    assert repr(v) == "nested_data_view([{'a': 1, 'b': 2}, {'b': 3, 'c': 4}])"

    assert v['a'] == [1]
    assert v['b'] == [2, 3]
    assert v['c'] == [4]

    with pytest.raises(KeyError):
        v['z']

    assert v.a == [1]
    assert v.b == [2, 3]
    assert v.c == [4]

    with pytest.raises(AttributeError):
        v.z

    assert v['a','b'] == [(1, 2), (1, 3)]
    assert v['b','a'] == [(2, 1), (3, 1)]
    assert v['b','c'] == [(3, 4)]
    assert v['c','b'] == [(4, 3)]
    assert v['a','c'] == [(1, 4)]
    assert v['c','a'] == [(4, 1)]

    assert v['a','b','c'] == [(1, 3, 4)]

    with pytest.raises(KeyError):
        v['a','z']

    assert v.flatten(0) == {'a': 1, 'b': 2}
    assert v.flatten(1) == {'a': 1, 'b': 3, 'c': 4}
    assert v.flatten(-1) == {'a': 1, 'b': 3, 'c': 4}

def test_info_view():
    p = [(0, 'a'), (1, 'b')]
    v = info_view(p)

    assert repr(v) == "info_view([(0, 'a'), (1, 'b')])"
    assert v[0] == 'a'
    assert len(v) == 2
    assert v.layers() == [(0, 'a'), (1, 'b')]
    assert v == ['a', 'b']

    v[1] = 'c'
    assert v[1] == 'c'
    assert p == [(0, 'a'), (-1, 'c')]

    del v[0]
    assert p == [(-1, 'c')]

    v.append('d')
    assert p == [(-1, 'c'), (-1, 'd')]

    v[:] = ['e', 'f']
    assert p == [(-1, 'e'), (-1, 'f')]

def test_reverse_view():
    l = [1, 2]
    v = reverse_view(l)

    assert repr(v) == '[2, 1]'
    assert len(v) == 2
    assert v[0] == 2
    assert v[1] == 1
    assert list(v) == [2, 1]

