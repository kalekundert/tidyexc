#!/usr/bin/env python3

import pytest
from tidyexc import utils, only_raise

class E1(Exception):
    pass

class E1a(E1):
    pass

class E2(Exception):
    pass

class E3(Exception):
    pass

@pytest.mark.parametrize(
        'only_err, raise_err, catch_err', [
            ([E1], E1,  E1),
            ([E1], E1a, E1a),
            ([E1], E2,  E1),

            ([E1a], E1,  E1a),
            ([E1a], E1a, E1a),
            ([E1a], E2,  E1a),

            ([E2], E1,  E2),
            ([E2], E1a, E2),
            ([E2], E2,  E2),

            ([E1, E2], E1,  E1),
            ([E1, E2], E1a, E1a),
            ([E1, E2], E2,  E2),
            ([E1, E2], E3,  E1),

            ([E2, E1], E1,  E1),
            ([E2, E1], E1a, E1a),
            ([E2, E1], E2,  E2),
            ([E2, E1], E3,  E2),
])
def test_only_raise(only_err, raise_err, catch_err):

    @only_raise(*only_err)
    def f(err):
        raise err

    with pytest.raises(catch_err):
        f(raise_err)

def test_only_raise_no_args_err():
    with pytest.raises(TypeError):
        @only_raise()
        def f():
            pass

def test_list_iadd():
    l = utils.list_iadd()

    l += "a"
    l += int
    l += ["c", "d"]

    assert l == ["a", int, "c", "d"]

