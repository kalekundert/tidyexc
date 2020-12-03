#!/usr/bin/env python3

class list_iadd(list):

    def __iadd__(self, other):
        if callable(other) or isinstance(other, str):
            self.append(other)
        else:
            self.extend(other)
        return self

def property_iadd(getter):

    def setter(self, x):
        if x is not getter(self):
            raise AttributeError("can't set attribute")

    return property(getter, setter)

def eval_template(template, data):
    try:
        if callable(template):
            return template(data)
        else:
            return template.format(**data)
    except Exception as err:
        return str(err)


