#!/usr/bin/env python3

import functools
from traceback import format_exc

class only_raise:
    """
    Guarantee that the decorated function can only raise the given type of 
    exception.

    Any unhandled exception raised by the decorated function will be caught and 
    re-raised using an exception of the given type. 
    """

    def __init__(self, err_cls):
        self.err_cls = err_cls

    def __call__(self, f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except self.err_cls as err:
                raise err from None
            except Exception as err:
                raise self.err_cls(str(err)) from err

        return wrapper


class iadd_mixin:

    def __iadd__(self, other):
        if callable(other) or isinstance(other, str):
            self.append(other)
        else:
            self.extend(other)
        return self

class list_iadd(iadd_mixin, list):
    pass

def property_iadd(getter):
    # Provide a more helpful error message if the user forgets to use `+=`.

    def setter(self, x):
        if x is not getter(self):
            raise AttributeError("can't set attribute, did you mean to use `+=`?")

    return property(getter, setter)

def eval_template(template, data):
    if callable(template):
        return template(data)
    else:
        return template.format(**data)
