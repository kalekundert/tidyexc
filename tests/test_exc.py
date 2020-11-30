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

    assert e.brief_str == "Brief"
    assert e.info_strs == [s['expected'], "Second line"]
    assert e.blame_strs == []
    assert e.hint_strs == []

    assert str(e) == f"""\
Brief
• {s['expected']}
• Second line
"""

@pytest.mark.parametrize("s", STRING_TYPES)
def test_blame(s):
    e = Error("Brief", **s['data'])
    e.blame += s['template']
    e.blame += "Second line"

    assert e.brief_str == "Brief"
    assert e.info_strs == []
    assert e.blame_strs == [s['expected'], "Second line"]
    assert e.hint_strs == []

    assert str(e) == f"""\
Brief
✖ {s['expected']}
✖ Second line
"""

@pytest.mark.parametrize("s", STRING_TYPES)
def test_hints(s):
    e = Error("Brief", **s['data'])
    e.hints += s['template']
    e.hints += "Second line"

    assert e.brief_str == "Brief"
    assert e.info_strs == []
    assert e.hint_strs == [s['expected'], "Second line"]
    assert e.blame_strs == []

    assert str(e) == f"""\
Brief
• {s['expected']}
• Second line
"""

def test_wrap(monkeypatch):
    import tidyexc.exc, os
    monkeypatch.setattr(
            tidyexc.exc, 'get_terminal_size',
            lambda: os.terminal_size((10, 1)),
    )

    ruler = "1 3 5 7 9 11 14 17"

    e = Error(ruler)
    e.info += ruler
    e.blame += ruler
    e.hints += ruler

    # Caret shows where the wrapping should occur:
    #    v
    assert str(e) == f"""\
1 3 5 7 9
11 14 17
• 1 3 5 7
  9 11 14
  17
✖ 1 3 5 7
  9 11 14
  17
• 1 3 5 7
  9 11 14
  17
"""

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
        a1, b1 = A("Brief"), B("Brief")

    a2, b2 = A("Brief"), B("Brief")

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

def test_add_info_nested():

    class A(Error):
        pass

    with A.add_info("Outer a={a} b={b} c={c}", a=1, b=1, c=1):
        a1 = A("Brief 1", a=2, b=2)
        a1.info += "Local a={a} b={b} c={c}"

        with A.add_info("Inner a={a} b={b} c={c}", a=2, b=2):
            a2 = A("Brief 2", a=3)
            a2.info += "Local a={a} b={b} c={c}"

    assert a1.info_strs == [
            "Outer a=2 b=2 c=1",
            "Local a=2 b=2 c=1",
    ]
    assert a2.info_strs == [
            "Outer a=3 b=2 c=1",
            "Inner a=3 b=2 c=1",
            "Local a=3 b=2 c=1",
    ]

            
