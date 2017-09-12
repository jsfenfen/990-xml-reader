import collections
#  Mostly from: http://stackoverflow.com/a/6027615


def flatten(d, parent_key='', sep='/'):
    items = []
    # print "flatten '%s'" % (d)
    if d:
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    else:
        return {}
