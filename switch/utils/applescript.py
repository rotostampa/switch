import types
from itertools import chain


class raw(str):
    pass


def to_applescript(s):
    if isinstance(s, (raw,)):
        return s
    if isinstance(s, (str,)):
        return '"{}"'.format(s.replace(r'"', r"\""))
    if isinstance(s, (int, float)):
        return "{}".format(s)
    if isinstance(s, bool):
        return str(s).lower()
    if s is None:
        return "null"
    if isinstance(s, dict):
        return "{{ {} }}".format(
            ",".join(("{}: {}".format(key, to_applescript(v)) for key, v in s.items()))
        )
    if isinstance(s, (list, tuple, set, frozenset, chain, types.GeneratorType)):
        return "{{ {} }}".format(",".join([to_applescript(v) for v in s]))
    raise TypeError("unrecognized {}".format(repr(s)))


def applescript_from_template(command, **context):
    return command.format(**{k: to_applescript(v) for k, v in context.items()})
