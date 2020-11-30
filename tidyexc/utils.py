#!/usr/bin/env python3

class list_iadd(list):

    def __iadd__(self, message):
        self.append(message)
        return self

def property_iadd(getter):

    def setter(self, x):
        if x is not getter(self):
            raise AttributeError("can't set attribute")

    return property(getter, setter)

def eval_template(template, data):
    if callable(template):
        return template(data)
    else:
        return template.format(**data)


