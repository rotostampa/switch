import logging
import os
import types
from itertools import chain


class ApplescriptResource:
    def __init__(self, path):
        self.path = path

    def raw_applescript(self):
        return 'get path to resource "{}"'.format(self.path)


def to_applescript(s):
    if hasattr(s, "to_applescript"):
        return to_applescript(s.to_applescript())
    elif hasattr(s, "raw_applescript"):
        return s.raw_applescript()
    elif isinstance(s, D):
        return "{}".format(s.cm)
    elif isinstance(s, six.string_types):
        return '"{}"'.format(s.replace(r'"', r"\""))
    elif isinstance(s, (int, float)):
        return "{}".format(s)
    elif isinstance(s, bool):
        return str(s).lower()
    elif s is None:
        return "null"
    elif isinstance(s, dict):
        return mark_safe(
            "{{ {} }}".format(
                ",".join(
                    ("{}: {}".format(key, to_applescript(v)) for key, v in s.items())
                )
            )
        )
    elif isinstance(s, (list, tuple, set, frozenset, chain, types.GeneratorType)):
        return "{{ {} }}".format(",".join([to_applescript(v) for v in s]))
    raise TypeError("unrecognized {}".format(repr(s)))


def applescript_from_template(template, context={}, **kwargs):
    defaults = {"constants": constants, "settings": settings}
    defaults.update(context)
    return applescript_from_string(render_to_string(template, defaults), **kwargs)


class ApplescriptException(Exception):
    pass


def applescript_from_string(command):
    for p in wait_for_process(process(["osascript", "-e", command])):
        if p.returncode:
            error = to_applescript(p.communicate()[0].decode("utf-8"))
            applescript_logger.error(command)
            raise ApplescriptException(error)
        else:
            applescript_logger.info(command)

        return p.communicate()[0].decode("utf-8")
