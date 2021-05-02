#!/usr/bin/env python3

import pytest
from tidyexc import utils, only_raise

class ParentError(Exception):
    pass

class ChildError(ParentError):
    pass

class UnrelatedError(Exception):
    pass

@pytest.mark.parametrize(
        'only_err, raise_err, catch_err', [
            (   ParentError,    ParentError,    ParentError),
            (   ParentError,     ChildError,     ChildError),
            (   ParentError, UnrelatedError,    ParentError),

            (    ChildError,    ParentError,     ChildError),
            (    ChildError,     ChildError,     ChildError),
            (    ChildError, UnrelatedError,     ChildError),

            (UnrelatedError,    ParentError, UnrelatedError),
            (UnrelatedError,     ChildError, UnrelatedError),
            (UnrelatedError, UnrelatedError, UnrelatedError),
])
def test_only_raise(only_err, raise_err, catch_err):

    @only_raise(only_err)
    def f(err):
        raise err

    with pytest.raises(catch_err):
        f(raise_err)

def test_list_iadd():
    l = utils.list_iadd()

    l += "a"
    l += int
    l += ["c", "d"]

    assert l == ["a", int, "c", "d"]

