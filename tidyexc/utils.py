#!/usr/bin/env python3

class list_iadd(list):

    def __iadd__(self, other):
        if callable(other) or isinstance(other, str):
            self.append(other)
        else:
            self.extend(other)
        return self

class dict_attr(dict):

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

def property_iadd(getter):

    def setter(self, x):
        if x is not getter(self):
            raise AttributeError("can't set attribute, did you mean to use `+=`?")

    return property(getter, setter)

def eval_template(template, data):
    try:
        if callable(template):
            return template(data)
        else:
            return template.format(**data)
    except Exception as err:
        return str(err)


