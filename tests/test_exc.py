#!/usr/bin/env python3

import pytest
from tidyexc import Error

STRING_TYPES = [
        dict(
            template="Fixed string",
            data={},
            expected="Fixed string",
        ),
        dict(
            template="Format string: {attr}",
            data=dict(attr="value"),
            expected="Format string: value",
        ),
        dict(
            template=lambda e: f"Callable: {e.attr}",
            data=dict(attr="value"),
            expected="Callable: value",
        ),
]

def test_raise():
    with pytest.raises(Error, match="Brief"):
        raise Error("Brief")

@pytest.mark.parametrize("s", STRING_TYPES)
def test_brief(s):
    e = Error(s['template'], **s['data'])

    assert e.brief_str == s['expected']
    assert e.info_strs == []
    assert e.blame_strs == []
    assert e.hint_strs == []

    assert str(e) == f"""\
{s['expected']}
"""

@pytest.mark.parametrize("s", STRING_TYPES)
def test_info(s):
    e = Error("Brief", **s['data'])

    e.info += s['template']
    e.info += "Second line"

    with pytest.raises(AttributeError, match=r"did you mean to use `\+\=`"):
        e.info = "Direct assignment"

    assert e.brief_str == "Brief"
    assert e.info_strs == [s['expected'], "Second line"]
    assert e.blame_strs == []
    assert e.hint_strs == []

    assert str(e) == f"""\
Brief
• {s['expected']}
• Second line
"""

def test_info_flatten():
    e = Error()
    e.info += "First line"
    e.info += lambda e: ["Second line", "Third line"]
    e.info += "Fourth line"

    assert e.info_strs == [
            "First line",
            "Second line",
            "Third line",
            "Fourth line",
    ]

@pytest.mark.parametrize("s", STRING_TYPES)
def test_blame(s):
    e = Error("Brief", **s['data'])
    e.blame += s['template']
    e.blame += "Second line"

    with pytest.raises(AttributeError, match=r"did you mean to use `\+\=`"):
        e.blame = "Direct assignment"

    assert e.brief_str == "Brief"
    assert e.info_strs == []
    assert e.blame_strs == [s['expected'], "Second line"]
    assert e.hint_strs == []

    assert str(e) == f"""\
Brief
✖ {s['expected']}
✖ Second line
"""

def test_blame_flatten():
    e = Error()
    e.blame += "First line"
    e.blame += lambda e: ["Second line", "Third line"]
    e.blame += "Fourth line"

    assert e.blame_strs == [
            "First line",
            "Second line",
            "Third line",
            "Fourth line",
    ]

@pytest.mark.parametrize("s", STRING_TYPES)
def test_hints(s):
    e = Error("Brief", **s['data'])
    e.hints += s['template']
    e.hints += "Second line"

    with pytest.raises(AttributeError, match=r"did you mean to use `\+\=`"):
        e.hints = "Direct assignment"

    assert e.brief_str == "Brief"
    assert e.info_strs == []
    assert e.hint_strs == [s['expected'], "Second line"]
    assert e.blame_strs == []

    assert str(e) == f"""\
Brief
• {s['expected']}
• Second line
"""

def test_hints_flatten():
    e = Error()
    e.hints += "First line"
    e.hints += lambda e: ["Second line", "Third line"]
    e.hints += "Fourth line"

    assert e.hint_strs == [
            "First line",
            "Second line",
            "Third line",
            "Fourth line",
    ]

def test_data():
    e = Error(a=1)

    assert 'a' in e.data
    assert 'b' not in e.data

    assert len(e.data) == 1

    assert e.data == {'a': 1}

    # getattr
    assert e.data.a == 1
    assert e.data['a'] == 1

    with pytest.raises(AttributeError):
        e.data.b
    with pytest.raises(KeyError):
        e.data['b']

    # setattr
    e.data.b = 2
    assert e.data == {'a': 1, 'b': 2}

    e.data['c'] = 3
    assert e.data == {'a': 1, 'b': 2, 'c': 3}

    # delattr
    del e.data.b
    assert e.data == {'a': 1, 'c': 3}

    del e.data['c']
    assert e.data == {'a': 1}

    with pytest.raises(AttributeError):
        del e.data.b
    with pytest.raises(KeyError):
        del e.data['b']

def test_data_setattr():

    class A(Error):
        pass

    with A.add_info(a=1):
        a = A(b=2)

    assert a.data == {'a': 1, 'b': 2}

    a.data = {'c': 3}
    assert a.data == {'a': 1, 'c': 3}

def test_nested_data_1():

    class A(Error):
        pass

    with A.add_info("", a=1, b=2):
        with A.add_info("", b=3, c=4):
            a = A(c=5, d=6)

    assert a.data == {'a': 1, 'b': 3, 'c': 5, 'd': 6}

    assert a.nested_data['a'] == [1]
    assert a.nested_data['b'] == [2, 3]
    assert a.nested_data['c'] == [4, 5]
    assert a.nested_data['d'] == [6]

    assert a.nested_data['a','b'] == [(1, 2), (1, 3)]
    assert a.nested_data['b','a'] == [(2, 1), (3, 1)]
    assert a.nested_data['b','c'] == [(3, 4), (3, 5)]
    assert a.nested_data['c','b'] == [(4, 3), (5, 3)]
    assert a.nested_data['c','d'] == [(5, 6)]
    assert a.nested_data['d','c'] == [(6, 5)]

def test_nested_data_2():
    # Simulate what might happen with a recursive function call (e.g. several 
    # levels defining the same exact parameters, with other levels defining 
    # unrelated parameters).  The previous test is more comprehensive, but this 
    # one is more representative.

    class A(Error):
        pass

    with A.add_info("", a=1, b=2):
        with A.add_info("", a=3, b=4):
            a = A(c=5)

    assert a.data == {'a': 3, 'b': 4, 'c': 5}

    assert a.nested_data['a'] == [1, 3]
    assert a.nested_data['b'] == [2, 4]
    assert a.nested_data['c'] == [5]

    assert a.nested_data['a','b'] == [(1, 2), (3, 4)]
    assert a.nested_data['b','a'] == [(2, 1), (4, 3)]
    assert a.nested_data['a','c'] == [(3, 5)]
    assert a.nested_data['c','a'] == [(5, 3)]
    assert a.nested_data['b','c'] == [(4, 5)]
    assert a.nested_data['c','b'] == [(5, 4)]

    assert a.nested_data['a','b','c'] == [(3, 4, 5)]

def test_iadd():
    e = Error()

    e.info += "a"
    e.info += lambda e: "b"
    e.info += ["c", "d"]
    e.info += ("e", "f")

    assert e.info_strs == ["a", "b", "c", "d", "e", "f"]

@pytest.mark.parametrize("s", STRING_TYPES)
def test_push_pop_info(s):

    class A(Error):
        pass

    class B(A):
        pass

    A.push_info(s['template'], **s['data'])
    B.push_info("x: {x}", x=1)
    B.push_info("y: {y}", y=2)
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
            "x: 1",
            "y: 2",
    ]

    with pytest.raises(IndexError):
        Error.pop_info()

    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
            "x: 1",
            "y: 2",
    ]

    B.pop_info()
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
            "x: 1",
    ]

    A.pop_info()
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
    ]
    assert b.info_strs == [
            "x: 1",
    ]

@pytest.mark.parametrize("s", STRING_TYPES)
def test_push_clear_info(s):

    class A(Error):
        pass

    class B(A):
        pass

    A.push_info(s['template'], **s['data'])
    B.push_info("x: {x}", x=1)
    B.push_info("y: {y}", y=2)
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
            "x: 1",
            "y: 2",
    ]

    Error.clear_info()
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
            "x: 1",
            "y: 2",
    ]

    B.clear_info()
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
            s['expected'],
    ]
    assert b.info_strs == [
            s['expected'],
    ]

    A.clear_info()
    a, b = A("Brief"), B("Brief")

    assert a.info_strs == [
    ]
    assert b.info_strs == [
    ]

@pytest.mark.parametrize("s", STRING_TYPES)
def test_add_info(s):

    class A(Error):
        pass

    class B(A):
        pass

    with A.add_info(s['template'], **s['data']):
        a1, b1 = A(), B()

    a2, b2 = A(), B()

    assert a1.info_strs == [
            s['expected']
    ]
    assert b1.info_strs == [
            s['expected']
    ]
    assert a2.info_strs == [
    ]
    assert b2.info_strs == [
    ]

    with B.add_info(s['template'], **s['data']):
        a1, b1 = A("Brief"), B("Brief")

    a2, b2 = A("Brief"), B("Brief")

    assert a1.info_strs == [
    ]
    assert b1.info_strs == [
            s['expected']
    ]
    assert a2.info_strs == [
    ]
    assert b2.info_strs == [
    ]

def test_add_info_multiple():

    class A(Error):
        pass

    with A.add_info(a=1, b=2):
        a1 = A()

    with A.add_info("{a}", a=3, b=4):
        a2 = A()

    with A.add_info("{a}", "{b}", a=5, b=6):
        a3 = A()

    assert a1.info_strs == []
    assert a2.info_strs == ["3"]
    assert a3.info_strs == ["5", "6"]

    assert a1.data == {'a': 1, 'b': 2}
    assert a2.data == {'a': 3, 'b': 4}
    assert a3.data == {'a': 5, 'b': 6}

def test_add_info_nested():

    class A(Error):
        pass

    with A.add_info("Outer a={a} b={b} c={c}", a=1, b=1, c=1):
        a1 = A(a=2, b=2)
        a1.info += "Local a={a} b={b} c={c}"

        with A.add_info("Inner a={a} b={b} c={c}", a=2, b=2):
            a2 = A(a=3)
            a2.info += "Local a={a} b={b} c={c}"

    assert a1.info_strs == [
            "Outer a=1 b=1 c=1",
            "Local a=2 b=2 c=1",
    ]
    assert a2.info_strs == [
            "Outer a=1 b=1 c=1",
            "Inner a=2 b=2 c=1",
            "Local a=3 b=2 c=1",
    ]

def test_add_info_nested_err():

    class A(Error):
        pass

    with A.add_info("Outer a={a} b={b}", a=1):
        a1 = A(b=2)

    with pytest.raises(KeyError):
        a1.info_strs

def test_put_info():
    e = Error(a=1, z=-1)
    e.info += "a={a}"
    e.put_info("a={a}")
    e.put_info("b={b}", b=2)
    e.put_info("b={b}", "c={c}", c=3)
    e.info += "z={z}"

    assert e.info_strs == [
            "a=1",
            "a=1",
            "b=2",
            "b=2",
            "c=3",
            "z=-1",
    ]

def test_put_info_nested():
    e = Error(a=1, b=1, c=1)
    e.put_info("a={a} b={b} c={c}", a=2, b=2)
    e.put_info("a={a} b={b} c={c}", a=3)

    assert e.info_strs == [
            "a=2 b=2 c=1",
            "a=3 b=2 c=1",
    ]

def test_str():
    e = Error("Brief")
    e.info += "Info"
    e.blame += "Blame"
    e.hints += "Hint"

    assert str(e) == """\
Brief
• Info
✖ Blame
• Hint
"""

def test_str_custom_bullet():

    class A(Error):
        info_bullet = 'i) '
        blame_bullet = 'x) '
        hint_bullet = '?) '

    a = A("Brief")
    a.info += "Info"
    a.blame += "Blame"
    a.hints += "Hint"

    assert str(a) == """\
Brief
i) Info
x) Blame
?) Hint
"""

def test_str_err():
    e = Error("{x}")
    e_str = str(e)

    assert "Error occurred while formatting Error:" in e_str
    assert "KeyError: 'x'" in e_str

def test_str_dict():
    # When I was using dotmap, I ran into a problem where dictionary data would 
    # be converted into a dotmap and rendered confusingly.  This test just 
    # makes sure that that behavior is eliminated.
    e = Error("{d}", d={'a': 1})
    assert str(e) == "{'a': 1}\n"

