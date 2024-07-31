import types
from itertools import chain


def to_applescript(s):

    if isinstance(s, (str,)):
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


def applescript_from_template(command, **context):
    return command.format(**{k: to_applescript(v) for k, v in context.items()})