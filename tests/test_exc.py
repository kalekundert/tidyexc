#!/usr/bin/env python3

import pytest
from tidyexc import Error, info

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


@pytest.mark.parametrize("s", STRING_TYPES)
def test_error_brief(s):
    e = Error(s['template'], **s['data'])

    assert e.brief_str == s['expected']
    assert e.info_strs == []
    assert e.blame_strs == []
    assert e.hint_strs == []

    assert str(e) == f"""\
{s['expected']}
"""

@pytest.mark.parametrize("s", STRING_TYPES)
def test_error_info(s):
    e = Error("Brief", **s['data'])
    debug(e.info)

    e.info += s['template']
    e.info += "Second line"

    debug(e.info)

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
def test_error_blame(s):
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
def test_error_hints(s):
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

def test_error_wrap(monkeypatch):
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
#        v
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
def test_info(s):
    with info(s['template'], **s['data']):
        e1 = Error("Brief 1")

    # Make sure the info doesn't persist outside the with block.
    e2 = Error("Brief 2")

    assert e1.info_strs == [s['expected']]
    assert e2.info_strs == []

def test_info_nested():
    def d(keys, value):
        return {k: value for k in keys}

    with info("Outer a={a} b={b} c={c}", a=1, b=1, c=1):
        e1 = Error("Brief 1", a=2, b=2)
        e1.info += "Local a={a} b={b} c={c}"

        with info("Inner a={a} b={b} c={c}", a=2, b=2):
            e2 = Error("Brief 2", a=3)
            e2.info += "Local a={a} b={b} c={c}"

    assert e1.info_strs == [
            "Outer a=2 b=2 c=1",
            "Local a=2 b=2 c=1",
    ]
    assert e2.info_strs == [
            "Outer a=3 b=2 c=1",
            "Inner a=3 b=2 c=1",
            "Local a=3 b=2 c=1",
    ]

            
