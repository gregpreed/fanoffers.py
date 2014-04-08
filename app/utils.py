def filter_dict(d, fields):
    return dict((k, v) for k, v in d.items() if k in fields)
